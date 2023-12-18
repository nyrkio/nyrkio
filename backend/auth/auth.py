# Copyright (c) 2024, Nyrkiö Oy

import os
from typing import Optional
import uuid

from beanie import PydanticObjectId
from fastapi import Depends, APIRouter, Request
from fastapi_users import BaseUserManager, FastAPIUsers
from fastapi_users.db import BeanieUserDatabase, ObjectIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)

from backend.db.db import User, get_user_db
from backend.auth.github import github_oauth


async def get_user_manager(user_db: BeanieUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

SECRET = os.environ.get("SECRET_KEY", "fooba")


def get_jwt_strategy() -> JWTStrategy:
    # Expires after a month
    expiration_secs = 3600 * 24 * 30
    return JWTStrategy(secret=SECRET, lifetime_seconds=expiration_secs)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

auth_router = APIRouter(prefix="/auth")
auth_router.include_router(
    fastapi_users.get_oauth_router(github_oauth, auth_backend, SECRET, redirect_url="http://localhost/api/v0/auth/github/callback"),
    prefix="/github",
    tags=["auth"],
)

auth_router.include_router(
    fastapi_users.get_auth_router(auth_backend, SECRET), prefix="/jwt", tags=["auth"]
)

current_active_user = fastapi_users.current_user(active=True)


@auth_router.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}


class UserManager(ObjectIDIDMixin, BaseUserManager[User, PydanticObjectId]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")
