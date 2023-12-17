# Copyright (c) 2024, Nyrkiö Oy

from abc import abstractmethod, ABC
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


class ConnectionStrategy(ABC):
    @abstractmethod
    def connect(self):
        pass

    def init_db(self):
        pass


class MongoDBStrategy(ConnectionStrategy):
    """
    Connect to a production MongoDB.
    """

    def connect(self):
        db_user = os.environ.get("DB_USER", None)
        db_password = os.environ.get("DB_PASSWORD", None)
        db_name = os.environ.get("DB_NAME", None)

        url = f"mongodb+srv://{db_user}:{db_password}@prod0.dn3tizr.mongodb.net/?retryWrites=true&w=majority"
        client = motor.motor_asyncio.AsyncIOMotorClient(
            url, uuidRepresentation="standard"
        )
        return client[db_name]


class TestDBStrategy(ConnectionStrategy):
    """
    Connect to a test DB for unit testing and add some test users.
    """

    def connect(self):
        client = AsyncMongoMockClient()
        return client.get_database("test")

    async def init_db(self):
        # Add test users
        from backend.auth.auth import UserManager

        user = UserCreate(
            email="john@foo.com", password="foo", is_active=True, is_verified=True
        )
        manager = UserManager(BeanieUserDatabase(User, OAuthAccount))
        await manager.create(user)


class DBStoreAlreadyInitialized(Exception):
    pass


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

    def __init__(self):
        self.strategy = None
        self.started = False

    def setup(self, connection_strategy: ConnectionStrategy):
        if self.strategy:
            raise DBStoreAlreadyInitialized()

        self.strategy = connection_strategy
        self.db = self.strategy.connect()

    async def startup(self):
        if self.started:
            raise DBStoreAlreadyInitialized()

        await init_beanie(database=self.db, document_models=[User])
        await self.strategy.init_db()
        self.started = True


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


# Will be patched by conftest.py if we're running tests
_TESTING = False


async def do_on_startup():
    store = DBStore()
    strategy = TestDBStrategy() if _TESTING else MongoDBStrategy()
    store.setup(strategy)
    await store.startup()
