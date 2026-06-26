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

# from backend.auth.email import read_template_file
from fastapi_users.authentication import JWTStrategy
import os

from backend.db.db import User, DBStore, get_user_db

auth_router = APIRouter(prefix="/auth")


# async def send_email(email: str, token: str, subject: str, msg: str):
#     """
#     Short circuit email sending, this just logs.
#     """
#     logging.info(
#         f"Email sending is disabled but would have sent: {email} {token} {subject} {msg}"
#     )


SECRET = os.environ.get("SECRET_KEY", "fooba")
SERVER_NAME = os.environ.get("SERVER_NAME", "localhost")
GOOGLE_RECAPTCHA_SECRETKEY = os.environ.get("GOOGLE_RECAPTCHA_SECRETKEY")
CF_SECRETKEY = os.environ.get("CF_SECRETKEY")
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
        token = data.get("cf-turnstile-response")
        remoteip = (
            request.headers.get("CF-Connecting-IP")
            or request.headers.get("X-Forwarded-For")
            or request.remote_addr
        )

        validation = await validate_turnstile(token, CF_SECRETKEY, remoteip)

        if not validation["success"]:
            raise HTTPException(
                status_code=400,
                detail=f"Blocked by CloudFlare: {validation['error-codes']}",
            )

        if user_create.oauth_accounts:
            logging.warning(user_create)
            raise Exception(
                "Someone tried to POST oauth credentials through the wrong door"
            )
        user_create.captcha_token = token
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

        # if not user.is_verified:
        #     await self.request_verify(user, request)

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        logging.info(f"User {user.id} has forgot their password. Reset token: {token}")
        reset_url = f"{SERVER_NAME}/forgot-password?token={token}"
        msg = read_template_file("forgot-password.html", reset_url=reset_url)
        await send_email(
            user.email, token, "Request to reset password. (nyrkio.com)", msg
        )

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
        cfToken = data.get("cf-turnstile-response")
        cfTokenGet = request.get("cf-turnstile-response")
        logging.info(data)
        logging.info(cfToken)
        logging.info(cfTokenGet)
        logging.info(user)
        if not user.captcha_token == cfToken:
            raise HTTPException(
                status_code=401,
                detail="Please provide cf-turnstile-response=xxxx in the URI query string. Same as you used the first time.",
            )

        verify_url = f"{SERVER_NAME}/api/v0/auth/verify-email/{token}"
        msg = read_template_file("verify-email.html", verify_url=verify_url)
        await send_email(
            user.email, token, "Verify your email (nyrkio.com new user creation)", msg
        )
        return {
            "status": "ok",
            "detail": "Sent email to given address, please click on the link",
        }

    async def get_by_github_username(self, github_username: str):
        return await self.user_db.get_by_github_username(github_username)

    # Copy pasted here because parent is buggy
    # async def get_by_oauth_account(
    #     self, oauth: str, account_id: str
    # ) -> Optional[UP_BEANIE]:
    #     """Get a single user by OAuth account id."""
    #     res = await super().get_by_oauth_account(oauth, account_id)
    #     print(res)
    #     print("---------------------------------------")
    #     return res
    #     res = await self.user_db.User.find_one(
    #         {
    #             "oauth_accounts.oauth_name": oauth,
    #             "oauth_accounts.account_id": account_id,
    #         }
    #     )
    #     print(res)
    #     return res

    # async def oauth_callback(
    #     self: "BaseUserManager[models.UOAP, models.ID]",
    #     oauth_name: str,
    #     access_token: str,
    #     account_id: str,
    #     account_email: str,
    #     expires_at: Optional[int] = None,
    #     refresh_token: Optional[str] = None,
    #     request: Optional[Request] = None,
    #     *,
    #     associate_by_email: bool = False,
    #     is_verified_by_default: bool = False,
    # ) -> models.UOAP:
    #     """
    #     Copied from fastapi_users.manager
    #
    #     Handle the callback after a successful OAuth authentication.
    #
    #     If the user already exists with this OAuth account, the token is updated.
    #
    #     If a user with the same e-mail already exists and `associate_by_email` is True,
    #     the OAuth account is associated to this user.
    #     Otherwise, the `UserNotExists` exception is raised.
    #
    #     If the user does not exist, it is created and the on_after_register handler
    #     is triggered.
    #
    #     :param oauth_name: Name of the OAuth client.
    #     :param access_token: Valid access token for the service provider.
    #     :param account_id: models.ID of the user on the service provider.
    #     :param account_email: E-mail of the user on the service provider.
    #     :param expires_at: Optional timestamp at which the access token expires.
    #     :param refresh_token: Optional refresh token to get a
    #     fresh access token from the service provider.
    #     :param request: Optional FastAPI request that
    #     triggered the operation, defaults to None
    #     :param associate_by_email: If True, any existing user with the same
    #     e-mail address will be associated to this user. Defaults to False.
    #     :param is_verified_by_default: If True, the `is_verified` flag will be
    #     set to `True` on newly created user. Make sure the OAuth Provider you're
    #     using does verify the email address before enabling this flag.
    #     Defaults to False.
    #     :return: A user.
    #     """
    #     oauth_account_dict = {
    #         "oauth_name": oauth_name,
    #         "access_token": access_token,
    #         "account_id": account_id,
    #         "account_email": account_email,
    #         "expires_at": expires_at,
    #         "refresh_token": refresh_token,
    #     }
    #
    #     try:
    #         user = await self.get_by_oauth_account(oauth_name, account_id)
    #         print(user)
    #         print("##########################################")
    #     except exceptions.UserNotExists:
    #         try:
    #             # Associate account
    #             user = await self.get_by_email(account_email)
    #             if not associate_by_email:
    #                 raise exceptions.UserAlreadyExists()
    #             user = await self.user_db.add_oauth_account(user, oauth_account_dict)
    #         except exceptions.UserNotExists:
    #             # Create account
    #             password = self.password_helper.generate()
    #             user_dict = {
    #                 "email": account_email,
    #                 "hashed_password": self.password_helper.hash(password),
    #                 "is_verified": is_verified_by_default,
    #             }
    #             user = await self.user_db.create(user_dict)
    #             user = await self.user_db.add_oauth_account(user, oauth_account_dict)
    #             await self.on_after_register(user, request)
    #     else:
    #         # Update oauth
    #         for existing_oauth_account in user.oauth_accounts:
    #             if (
    #                 existing_oauth_account.account_id == account_id
    #                 and existing_oauth_account.oauth_name == oauth_name
    #             ):
    #                 user = await self.user_db.update_oauth_account(
    #                     user, existing_oauth_account, oauth_account_dict
    #                 )
    #
    #     return user


async def validate_turnstile(token, secret, remoteip=None):
    url = "https://challenges.cloudflare.com/turnstile/v0/siteverify"

    data = {"secret": secret, "response": token}

    if remoteip:
        data["remoteip"] = remoteip

    client = httpx.AsyncClient()
    response = await client.post(
        url,
        data=data,
    )
    if response.status_code != 200:
        return {"success": False}

    return response.json()


# Copied from google-recaptcha which is a Flask app, turns out...
# request.form['g-recaptcha-response']
async def verify_recaptcha(
    g_recaptcha_response: str, remoteip: Optional[str] = None, require_min_score=0.4
):
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
    is_success = res.get("success", False)
    is_above_min_score = True
    if require_min_score is not None and require_min_score:
        is_above_min_score = float(res.get("score", -1.0)) >= require_min_score

    return is_success and is_above_min_score, res


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
