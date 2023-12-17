# Copyright (c) 2024, Nyrkiö Oy

import os
from typing import List

import motor.motor_asyncio
from mongomock_motor import AsyncMongoMockClient
from beanie import Document, PydanticObjectId, init_beanie
from fastapi_users.db import BaseOAuthAccount, BeanieBaseUser, BeanieUserDatabase
from fastapi_users import schemas
from pydantic import Field

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # noqa: E501
        "disabled": False,
        "is_admin": False,
    }
}


class DBStore(object):
    """
    A simple in-memory database for storing users.

    This is a singleton class, so there can only be one instance of it.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DBStore, cls).__new__(cls)
        return cls._instance

    async def startup(self):
        await init_beanie(database=self.db, document_models=[User])


class MongoDBStore(DBStore):
    """
    A MongoDB-backed DBStore.
    """

    def __init__(self):
        super(MongoDBStore, self).__init__()
        self.db_user = os.environ.get("DB_USER", None)
        self.db_password = os.environ.get("DB_PASSWORD", None)
        self.db_name = os.environ.get("DB_NAME", None)

        url = f"mongodb+srv://{self.db_user}:{self.db_password}@prod0.dn3tizr.mongodb.net/?retryWrites=true&w=majority"
        client = motor.motor_asyncio.AsyncIOMotorClient(
            url, uuidRepresentation="standard"
        )
        self.db = client[self.db_name]


class OAuthAccount(BaseOAuthAccount):
    pass


class User(BeanieBaseUser, Document):
    oauth_accounts: List[OAuthAccount] = Field(default_factory=list)


async def get_user_db():
    yield BeanieUserDatabase(User, OAuthAccount)


class UserRead(schemas.BaseUser[PydanticObjectId]):
    pass


class UserCreate(schemas.BaseUserCreate):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    pass


class TestDBStore(DBStore):
    """
    A test DBStore that doesn't persist data between tests.
    """

    def __init__(self):
        super(TestDBStore, self).__init__()
        client = AsyncMongoMockClient()
        self.db = client.get_database("test")

    async def startup(self):
        # Call super method to initialize Beanie
        await super(TestDBStore, self).startup()
        # Add test users
        from backend.auth.auth import UserManager

        user = UserCreate(
            email="john@foo.com", password="foo", is_active=True, is_verified=True
        )
        manager = UserManager(BeanieUserDatabase(User, OAuthAccount))
        await manager.create(user)


# Will be patched by conftest.py if we're running tests
TESTING = os.environ.get("NYRKIO_TESTING", False)


async def do_on_startup():
    TESTING = True
    if TESTING:
        store = TestDBStore()
    else:
        store = MongoDBStore()
    await store.startup()
