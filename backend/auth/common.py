import httpx
import logging

from fastapi import APIRouter, Depends, Request, HTTPException

# from fastapi_users import BaseUserManager, BaseUserDatabase
from fastapi_users import models, schemas
from fastapi_users.manager import BaseUserManager, BaseUserDatabase
from fastapi_users.authentication import (
    AuthenticationBackend,
    #    BearerTransport,
)
from fastapi_users.jwt import generate_jwt, decode_jwt
from backend.auth.bearer_or_body_transport import BearerOrBodyTransport

from typing import Optional
from beanie import PydanticObjectId
from fastapi_users.db import BeanieUserDatabase, ObjectIDIDMixin
from backend.auth.email import send_email, read_template_file
from fastapi_users.authentication import JWTStrategy
import os

from backend.db.db import User, DBStore, get_user_db

auth_router = APIRouter(prefix="/auth")


SECRET = os.environ.get("SECRET_KEY", "fooba")
SERVER_NAME = os.environ.get("SERVER_NAME", "localhost")
GOOGLE_RECAPTCHA_SECRETKEY = os.environ.get("GOOGLE_RECAPTCHA_SECRETKEY")
# The sitekey is just for the frontend to do its api request
# GOOGLE_RECAPTCHA_SITEKEY = os.environ.get("GOOGLE_RECAPTCHA_SITEKEY")


async def get_user_manager(user_db: BeanieUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


class UserManager(ObjectIDIDMixin, BaseUserManager[User, PydanticObjectId]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    # Prevent creating users with a billing plan.
    # TODO: is check what's the deal with oauth and others when they come this far
    async def create(
        self,
        user_create: schemas.UC,
        safe: bool = False,
        request: Optional[Request] = None,
        *args,
        **kwargs,
    ) -> models.UP:
        if os.environ.get("NYRKIO_TESTING", False):
            return await super().create(user_create, *args, **kwargs)

        # Note this is unauthenticated web form. Before writing to db, protect yourself.
        # No seriously, postmark will close the account immediately if you don't
        if request is None:
            raise ValueError(
                "Can't ... if stupid framework doesn't share the request so I can get the recaptcha fields."
            )
        data = await request.json()
        g_recaptcha_response = data.get("g-recaptcha-response")
        remoteip = request.client.host
        if not await verify_recaptcha(g_recaptcha_response, remoteip):
            raise HTTPException(status_code=400, detail="Blocked by ReCaptcha")
        else:
            self._already_checked_recaptcha = g_recaptcha_response

        if user_create.oauth_accounts:
            logging.warning(user_create)
            raise Exception(
                "Someone tried to POST oauth credentials through the wrong door"
            )

        user_create.billing = None
        user_create.billing_runners = None
        user_create.slack = None
        logging.info(
            "Creating new user with billing, billing_runners and slack blocked even if the generated api would make you believe anyone can just set those..."
        )
        logging.info(user_create)
        logging.info(user_create.model_dump())
        return await super().create(user_create, *args, **kwargs)

    async def create_cph(
        self,
        user_create: schemas.UC,
        safe: bool = False,
        request: Optional[Request] = None,
        *args,
        **kwargs,
    ) -> models.UP:
        logging.info(f"Create new CPH user {user_create.github_username}")
        if user_create.oauth_accounts:
            logging.warning(user_create)
            raise Exception(
                "Someone tried to POST oauth credentials through the wrong door"
            )

        user_create.billing = None
        user_create.billing_runners = None
        user_create.slack = None
        logging.info(user_create)
        logging.info(user_create.model_dump())
        return await super().create(user_create, *args, **kwargs)

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        logging.info(f"New User {user.id} {user.email} registered.")
        store = DBStore()
        await store.add_default_data(user)

        if not user.is_verified:
            await self.request_verify(user, request)

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        logging.info(f"User {user.id} has forgot their password. Reset token: {token}")
        reset_url = f"{SERVER_NAME}/forgot-password?token={token}"
        msg = read_template_file("forgot-password.html", reset_url=reset_url)
        await send_email(user.email, token, "nyrkio:com", msg)

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        logging.info(
            f"Verification requested for user {user.id} {user.email}. Verification token: {token}"
        )
        # Note this is unauthenticated web form. Before sending email, protect yourself.
        # No seriously, postmark will close the account immediately if you don't
        if request is None:
            raise ValueError(
                "Can't send verification email if stupid framework doesn't share the request so I can get the recaptcha fields."
            )
        data = await request.json()
        g_recaptcha_response = data.get("g-recaptcha-response")
        if (
            not self._already_checked_recaptcha
            and self._already_checked_recaptcha == g_recaptcha_response
        ):
            remoteip = request.client.host
            if g_recaptcha_response is not None and not await verify_recaptcha(
                g_recaptcha_response, remoteip
            ):
                raise HTTPException(status_code=400, detail="Blocked by ReCaptcha ..")

        verify_url = f"{SERVER_NAME}/api/v0/auth/verify-email/{token}"
        msg = read_template_file("verify-email.html", verify_url=verify_url)
        await send_email(user.email, token, "Verify your email", msg)
        return {
            "status": "ok",
            "detail": "Sent email to given address, please click on the link",
        }

        raise HTTPException(status_code=400, detail="Blocked by ReCaptcha ...")

    async def get_by_github_username(self, github_username: str):
        return await self.user_db.get_by_github_username(github_username)


# Copied from google-recaptcha which is a Flask app, turns out...
# request.form['g-recaptcha-response']
async def verify_recaptcha(g_recaptcha_response: str, remoteip: Optional[str] = None):
    url = "https://www.google.com/recaptcha/api/siteverify"

    data = {
        "secret": GOOGLE_RECAPTCHA_SECRETKEY,
        "response": g_recaptcha_response,
    }
    # if remoteip:
    #     data["remoteip"] = remoteip

    logging.info(data)

    client = httpx.AsyncClient()
    response = await client.post(
        url,
        data=data,
    )
    if response.status_code != 200:
        logging.error(
            "Google ReCaptcha backend returned HTTP status " + response.status_code
        )
        return False
    res = response.json()
    logging.info(res)
    return res.get("success", False)


class CphJWTStrategy(JWTStrategy):
    """
    If github user Alice submitted a Pull Request against github.com/acme/tools
    """

    async def write_token(
        self,
        user: BaseUserDatabase,
        is_cph_user: bool = False,
        repo_owner: Optional[str] = None,
        github_username: Optional[str] = None,
    ) -> str:
        data = {
            "sub": str(user.id),
            "aud": self.token_audience,
            "is_cph_user": is_cph_user,
            "repo_owner": repo_owner,
            "github_username": user.github_username if user.github_username else None,
        }
        return generate_jwt(
            data, self.encode_key, self.lifetime_seconds, algorithm=self.algorithm
        )

    def read_token_and_i_mean_token(self, token):
        data = decode_jwt(
            token, self.decode_key, self.token_audience, algorithms=[self.algorithm]
        )
        return data


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=None)


def get_short_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=300)


def get_cph_jwt_strategy() -> JWTStrategy:
    return CphJWTStrategy(secret=SECRET, lifetime_seconds=300)


bearer_transport = BearerOrBodyTransport(tokenUrl="auth/jwt/login")

jwt_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)
