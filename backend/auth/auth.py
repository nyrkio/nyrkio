# Copyright (c) 2024, Nyrkiö Oy

import jwt
import os
from typing import Optional, Tuple
import uuid

from beanie import PydanticObjectId
from fastapi import Depends, APIRouter, Request, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi_users import BaseUserManager, FastAPIUsers, models, exceptions, schemas
from fastapi_users.db import BeanieUserDatabase, ObjectIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    CookieTransport,
    JWTStrategy,
)
from fastapi_users.exceptions import UserAlreadyExists
from fastapi_users.router.oauth import STATE_TOKEN_AUDIENCE
from fastapi_users.router.common import ErrorCode

from httpx_oauth.integrations.fastapi import OAuth2AuthorizeCallback
from httpx_oauth.oauth2 import OAuth2Token

from backend.db.db import User, get_user_db, UserRead, UserCreate, DBStore
from backend.auth.github import github_oauth
from backend.auth.email import send_email, read_template_file


async def get_user_manager(user_db: BeanieUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")
COOKIE_NAME = "auth_cookie"
cookie_transport = CookieTransport(cookie_name=COOKIE_NAME)

SECRET = os.environ.get("SECRET_KEY", "fooba")
SERVER_NAME = os.environ.get("SERVER_NAME", "localhost")


def get_jwt_strategy() -> JWTStrategy:
    # Expires after a month
    expiration_secs = 3600 * 24 * 30
    return JWTStrategy(secret=SECRET, lifetime_seconds=expiration_secs)


jwt_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

cookie_backend = AuthenticationBackend(
    name="cookie",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager, [jwt_backend, cookie_backend]
)

REDIRECT_URI = "http://localhost/api/v0/auth/github/mycallback"
auth_router = APIRouter(prefix="/auth")
auth_router.include_router(
    fastapi_users.get_oauth_router(
        github_oauth,
        jwt_backend,
        SECRET,
        redirect_url=REDIRECT_URI,
    ),
    prefix="/github",
    tags=["auth"],
)

auth_router.include_router(
    fastapi_users.get_auth_router(jwt_backend, SECRET), prefix="/jwt", tags=["auth"]
)

auth_router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    tags=["auth"],
)

auth_router.include_router(
    fastapi_users.get_verify_router(UserRead),
    tags=["auth"],
)

auth_router.include_router(
    fastapi_users.get_reset_password_router(),
    tags=["auth"],
)

current_active_user = fastapi_users.current_user(active=True)


@auth_router.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}


oauth2_authorize_callback = OAuth2AuthorizeCallback(
    github_oauth, redirect_url=REDIRECT_URI
)


@auth_router.get("/verify-email/{token}")
async def verify_email(
    token: str,
    user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
):
    try:
        user = await user_manager.verify(token, None)
        schema = schemas.model_validate(UserRead, user)
        if user.is_verified:
            return RedirectResponse("/login")
        return schema

    except (exceptions.InvalidVerifyToken, exceptions.UserNotExists):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.VERIFY_USER_BAD_TOKEN,
        )
    except exceptions.UserAlreadyVerified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.VERIFY_USER_ALREADY_VERIFIED,
        )


@auth_router.get("/github/mycallback", include_in_schema=False)
async def github_callback(
    request: Request,
    access_token_state: Tuple[OAuth2Token, str] = Depends(oauth2_authorize_callback),
    user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
):
    token, state = access_token_state
    # Verify that we can decode the token so know it's valid
    try:
        jwt.decode(state, SECRET, audience=[STATE_TOKEN_AUDIENCE], algorithms=["HS256"])
    except jwt.DecodeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    account_id, account_email = await github_oauth.get_id_email(token["access_token"])

    if account_email is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.OAUTH_NOT_AVAILABLE_EMAIL,
        )

    try:
        user = await user_manager.oauth_callback(
            github_oauth.name,
            token["access_token"],
            account_id,
            account_email,
            token.get("expires_at"),
            token.get("refresh_token"),
            request,
            associate_by_email=False,
            is_verified_by_default=False,
        )
    except UserAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.OAUTH_USER_ALREADY_EXISTS,
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.LOGIN_BAD_CREDENTIALS,
        )

    response = await jwt_backend.login(get_jwt_strategy(), user)
    await user_manager.on_after_login(user, request, response)
    cookie_token = await get_jwt_strategy().write_token(user)
    response = RedirectResponse("/")
    response.set_cookie(COOKIE_NAME, cookie_token, httponly=True, samesite="lax")
    return response


class UserManager(ObjectIDIDMixin, BaseUserManager[User, PydanticObjectId]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")
        store = DBStore()
        await store.add_default_data(user)

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")
        verify_url = f"{SERVER_NAME}/api/v0/auth/verify-email/{token}"
        msg = read_template_file("verify-email.html", verify_url=verify_url)
        await send_email(user.email, token, "Verify your email", msg)
