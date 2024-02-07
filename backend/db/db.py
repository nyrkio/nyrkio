# Copyright (c) 2024, Nyrkiö Oy

from abc import abstractmethod, ABC
import os
from typing import Dict, List

import motor.motor_asyncio
from mongomock_motor import AsyncMongoMockClient
from beanie import Document, PydanticObjectId, init_beanie
from fastapi_users.db import BaseOAuthAccount, BeanieBaseUser, BeanieUserDatabase
from fastapi_users import schemas
from pydantic import Field


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


class ConnectionStrategy(ABC):
    @abstractmethod
    def connect(self):
        pass

    async def init_db(self):
        pass


class MongoDBStrategy(ConnectionStrategy):
    """
    Connect to a production MongoDB.
    """

    def connect(self):
        db_name = os.environ.get("DB_NAME", None)
        url = os.environ.get("DB_URL", None)
        client = motor.motor_asyncio.AsyncIOMotorClient(
            url, uuidRepresentation="standard"
        )
        return client[db_name]


class MockDBStrategy(ConnectionStrategy):
    """
    Connect to a test DB for unit testing and add some test users.
    """

    def __init__(self):
        self.user = None
        self.connection = None

    def connect(self):
        client = AsyncMongoMockClient()
        self.connection = client.get_database("test")
        return self.connection

    async def init_db(self):
        # Add test users
        from backend.auth.auth import UserManager

        # Add some default data
        await self.connection.default_data.insert_many(
            [
                {"test_name": "default_benchmark", "foo": "bar"},
            ]
        )

        user = UserCreate(
            id=1, email="john@foo.com", password="foo", is_active=True, is_verified=True
        )
        manager = UserManager(BeanieUserDatabase(User, OAuthAccount))
        self.user = await manager.create(user)

    def get_test_user(self):
        assert self.user, "init_db() must be called first"
        return self.user


class DBStoreAlreadyInitialized(Exception):
    pass


class DBStore(object):
    """
    A simple in-memory database for storing users.

    This is a singleton class, so there can only be one instance of it.

    This class is responsible for translating back and forth between documents
    using the MongoDB schema and the JSON data we return to HTTP clients. For
    example, we add the user ID to all documents along with the version of the
    document schema, and we don't want to leak these details when returning
    results in get_results(). See sanitize_results() for more info.
    """

    _instance = None

    # The version of the schema for test results. This version is independent of the
    # version of the API or Nyrkiö release. It is only incremented when the schema
    # for test results changes.
    _VERSION = 1

    # A list of keys that we don't want to return to the client but that are a
    # necessary part of the document schema.
    _internal_keys = ("_id", "user_id", "version", "test_name")

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

    @staticmethod
    def create_doc_with_metadata(doc: Dict, user: User, test_name: str) -> Dict:
        """
        Return a new document with added metadata, e.g. the version of the schema and the user ID.

        This is used when storing documents in the DB.

          user_id -> The ID of the user who created the document
          version -> The version of the schema for the document
          test_name -> The name of the test
        """
        d = dict(doc)
        d["user_id"] = user.id
        d["version"] = DBStore._VERSION
        d["test_name"] = test_name
        return d

    async def add_results(self, user: User, test_name: str, results: List[Dict]):
        """
        Create the representation of test results for storing in the DB, e.g. add
        metadata like user id and version of the schema.
        """
        new_list = [
            DBStore.create_doc_with_metadata(r, user, test_name) for r in results
        ]
        test_results = self.db.test_results
        await test_results.insert_many(new_list)

    async def get_results(self, user: User, test_name: str) -> List[Dict]:
        """
        Retrieve test results for a given user and test name. The results are
        guaranteed to be sorted by timestamp in ascending order.

        If no results are found, return an empty list.
        """
        test_results = self.db.test_results

        # Strip out the internal keys
        exclude_projection = {key: 0 for key in self._internal_keys}

        # TODO(matt) We should read results in batches, not all at once
        results = (
            await test_results.find(
                {"user_id": user.id, "test_name": test_name}, exclude_projection
            )
            .sort("timestamp")
            .to_list(None)
        )

        return results

    async def get_test_names(self, user: User) -> List[str]:
        """
        Get a list of all test names for a given user.

        Returns an empty list if no results are found.
        """
        test_results = self.db.test_results
        return await test_results.distinct("test_name", {"user_id": user.id})

    async def delete_all_results(self, user: User):
        """
        Delete all results for a given user.

        If no results are found, do nothing.
        """
        test_results = self.db.test_results
        await test_results.delete_many({"user_id": user.id})

    async def delete_result(self, user: User, test_name: str, timestamp: int):
        """
        Delete a single result for a given user, test name, and timestamp.

        If no matching results are found, do nothing.
        """
        test_results = self.db.test_results
        if timestamp:
            await test_results.delete_one(
                {"user_id": user.id, "test_name": test_name, "timestamp": timestamp}
            )
        else:
            await test_results.delete_many({"user_id": user.id, "test_name": test_name})

    async def add_default_data(self, user: User):
        """
        Add default data for a new user.
        """
        cursor = self.db.default_data.find()
        default_results = []
        for cursor in await cursor.to_list(None):
            d = dict(cursor)
            del d["_id"]
            default_results.append(d)

        if not default_results:
            return

        # TODO(Matt) We assume that all default data has the same test name
        # but this won't be true when we add more tests
        test_name = default_results[0]["test_name"]
        await self.add_results(user, test_name, default_results)

    async def get_default_test_names(self):
        """
        Get a list of all test names for the default data.

        Returns an empty list if no results are found.
        """
        default_data = self.db.default_data
        return await default_data.distinct("test_name")

    async def get_default_data(self, test_name):
        """
        Get the default data for a new user.
        """
        # Strip out the internal keys
        exclude_projection = {key: 0 for key in self._internal_keys}

        # TODO(matt) We should read results in batches, not all at once
        default_data = self.db.default_data
        cursor = default_data.find({"test_name": test_name}, exclude_projection)
        return await cursor.sort("timestamp").to_list(None)

    #
    # Change detection can be disabled for metrics on a per-user, per-test basis.
    # This is useful when certain metrics are too noisy to be useful and users just
    # want to outright not used them.
    #
    # A metric is "disabled" by adding a document to the "metrics" collection. It can
    # be re-enabled by removing the document.
    #
    async def disable_changes(self, user: User, test_name: str, metrics: List[str]):
        """
        Disable changes for a given user, test, metric combination.
        """
        for metric in metrics:
            await self.db.metrics.insert_one(
                {
                    "user_id": user.id,
                    "test_name": test_name,
                    "metric_name": metric,
                    "is_disabled": True,
                }
            )

    async def enable_changes(self, user: User, test_name: str, metrics: List[str]):
        """
        Enable changes for a given user, test, metric combination.
        """
        if not metrics:
            # Enable all metrics
            await self.db.metrics.delete_many(
                {"user_id": user.id, "test_name": test_name, "is_disabled": True}
            )
        else:
            for metric in metrics:
                await self.db.metrics.delete_one(
                    {
                        "user_id": user.id,
                        "test_name": test_name,
                        "metric_name": metric,
                        "is_disabled": True,
                    }
                )

    async def get_disabled_metrics(self, user: User, test_name: str) -> List[str]:
        """
        Get a list of disabled metrics for a given user and test name.

        Returns an empty list if no results are found.
        """
        metrics = self.db.metrics
        return await metrics.distinct(
            "metric_name", {"user_id": user.id, "test_name": test_name}
        )


# Will be patched by conftest.py if we're running tests
_TESTING = False


async def do_on_startup():
    store = DBStore()
    strategy = MockDBStrategy() if _TESTING else MongoDBStrategy()
    store.setup(strategy)
    await store.startup()
