from fastapi import APIRouter, Depends, Request
from fastapi_users import BaseUserManager
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
)

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


async def get_user_manager(user_db: BeanieUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


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

    async def get_by_github_username(self, github_username: str):
        return await self.user_db.get_by_github_username(github_username)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=None)


def get_short_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=300)


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

jwt_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)
