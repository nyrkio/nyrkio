# Copyright (c) 2024, Nyrkiö Oy

from abc import abstractmethod, ABC
from collections import OrderedDict
import logging
import os
from typing import Dict, List, Optional, Any

import motor.motor_asyncio
from pymongo.errors import BulkWriteError
from mongomock_motor import AsyncMongoMockClient
from beanie import Document, PydanticObjectId, init_beanie
from fastapi_users.db import BaseOAuthAccount, BeanieBaseUser, BeanieUserDatabase
from fastapi_users import schemas
from pydantic import Field


class OAuthAccount(BaseOAuthAccount):
    organizations: Optional[List[Dict]] = Field(default_factory=list)


class User(BeanieBaseUser, Document):
    oauth_accounts: Optional[List[OAuthAccount]] = Field(default_factory=list)
    slack: Optional[Dict[str, Any]] = Field(default_factory=dict)


async def get_user_db():
    yield BeanieUserDatabase(User, OAuthAccount)


class UserRead(schemas.BaseUser[PydanticObjectId]):
    oauth_accounts: Optional[List[OAuthAccount]] = Field(default_factory=list)
    slack: Optional[Dict[str, Any]] = Field(default_factory=dict)


class UserCreate(schemas.BaseUserCreate):
    oauth_accounts: Optional[List[OAuthAccount]] = Field(default_factory=list)
    slack: Optional[Dict[str, Any]] = Field(default_factory=dict)


class UserUpdate(schemas.BaseUserUpdate):
    oauth_accounts: Optional[List[OAuthAccount]] = Field(default_factory=list)
    slack: Optional[Dict[str, Any]] = Field(default_factory=dict)


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

    DEFAULT_DATA = {
        "timestamp": 123456,
        "attributes": {
            "git_repo": "https://github.com/nyrkio/nyrkio",
            "branch": "main",
            "git_commit": "123456",
        },
    }

    async def init_db(self):
        # Add test users
        from backend.auth.auth import UserManager

        user = UserCreate(
            id=1, email="john@foo.com", password="foo", is_active=True, is_verified=True
        )
        manager = UserManager(BeanieUserDatabase(User, OAuthAccount))
        self.user = await manager.create(user)

        # Add some default data
        result = DBStore.create_doc_with_metadata(
            MockDBStrategy.DEFAULT_DATA, self.user.id, "default_benchmark"
        )
        await self.connection.default_data.insert_one(result)

        # Usually a new user would get the default data automatically,
        # but since we added the default data after the user was created,
        # we need to add it manually.
        await self.connection.test_results.insert_one(result)

        su = UserCreate(
            id=2,
            email="admin@foo.com",
            password="admin",
            is_active=True,
            is_verified=True,
            is_superuser=True,
        )
        await manager.create(su)

    def get_test_user(self):
        assert self.user, "init_db() must be called first"
        return self.user


class DBStoreAlreadyInitialized(Exception):
    pass


class DBStoreResultExists(Exception):
    def __init__(self, duplicate_key):
        self.key = duplicate_key


class DBStoreMissingRequiredKeys(Exception):
    """
    Raised when the DBStore is unable to build a primary key because the
    result is missing required keys.
    """

    def __init__(self, missing_keys):
        self.missing_keys = missing_keys


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
    def create_doc_with_metadata(doc: Dict, id: Any, test_name: str) -> Dict:
        """
        Return a new document with added metadata, e.g. the version of the schema and the user ID.

        This is used when storing documents in the DB.

          id -> The ID of the user who created the document. Can also be a GitHub org ID
          version -> The version of the schema for the document
          test_name -> The name of the test

        We also build a primary key from the git_repo, branch, git_commit,
        test_name, timestamp, and user ID. If any of the keys are missing,
        raise a DBStoreMissingKeys exception.
        """
        d = dict(doc)

        missing_keys = []

        # Make sure all the required keys are present
        for key in ["timestamp", "attributes"]:
            if key not in d:
                missing_keys.append(key)

        attr_keys = ("git_repo", "branch", "git_commit")
        if "attributes" not in d:
            # They're all missing
            missing_keys.extend([f"attributes.{k}" for k in attr_keys])
            missing_keys.append(missing_keys)
        else:
            for key in attr_keys:
                if key not in d["attributes"]:
                    missing_keys.append(f"attributes.{key}")

        if len(missing_keys) > 0:
            raise DBStoreMissingRequiredKeys(missing_keys)

        # The id is built from the git_repo, branch, test_name, timestamp and
        # git commit. This tuple should be unique for each test result.
        #
        # NOTE The ordering of the keys is important for MongoDB -- a different
        # order represents a different primary key.
        primary_key = OrderedDict(
            {
                "git_repo": d["attributes"]["git_repo"],
                "branch": d["attributes"]["branch"],
                "git_commit": d["attributes"]["git_commit"],
                "test_name": test_name,
                "timestamp": d["timestamp"],
                "user_id": id,
            }
        )

        d["_id"] = primary_key
        d["user_id"] = id
        d["version"] = DBStore._VERSION
        d["test_name"] = test_name
        return d

    async def add_results(self, id: Any, test_name: str, results: List[Dict]):
        """
        Create the representation of test results for storing in the DB, e.g. add
        metadata like user id and version of the schema.

        If the user tries to add a result that already exists, raise a
        DBStoreResultExists exception.
        """
        new_list = [DBStore.create_doc_with_metadata(r, id, test_name) for r in results]
        test_results = self.db.test_results

        try:
            await test_results.insert_many(new_list)
        except BulkWriteError as e:
            if e.details["writeErrors"][0]["code"] == 11000:
                duplicate_key = e.details["writeErrors"][0]["op"]["_id"]

                # Don't leak user_id to the client. Anyway, it's not JSON
                # serializable.
                del duplicate_key["user_id"]

                raise DBStoreResultExists(duplicate_key)

    async def get_results(self, id: Any, test_name: str) -> List[Dict]:
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
                {"user_id": id, "test_name": test_name}, exclude_projection
            )
            .sort("timestamp")
            .to_list(None)
        )

        return results

    async def get_test_names(self, id: Any = None) -> Any:
        """
        Get a list of all test names for a given user. If id is None then
        return a dictionary of all test names for all users.

        Returns an empty list if no results are found.
        """
        test_results = self.db.test_results
        if id:
            return await test_results.distinct("test_name", {"user_id": id})
        else:
            results = await test_results.aggregate(
                [
                    {
                        "$group": {
                            "_id": "$user_id",
                            "test_names": {"$addToSet": "$test_name"},
                        }
                    }
                ]
            ).to_list(None)

            # Convert the user_id to a user email
            user_results = {}
            for result in results:
                user = await self.db.User.find_one({"_id": result["_id"]})
                if not user:
                    logging.error(f"No user found for id {result['_id']}")
                    continue

                email = user["email"]
                user_results[email] = result["test_names"]
            return user_results

    async def delete_all_results(self, user: User):
        """
        Delete all results for a given user.

        If no results are found, do nothing.
        """
        test_results = self.db.test_results
        await test_results.delete_many({"user_id": user.id})

    async def delete_result(self, id: Any, test_name: str, timestamp: int):
        """
        Delete a single result for a given user, test name, and timestamp.

        If no matching results are found, do nothing.
        """
        test_results = self.db.test_results
        if timestamp:
            await test_results.delete_one(
                {"user_id": id, "test_name": test_name, "timestamp": timestamp}
            )
        else:
            await test_results.delete_many({"user_id": id, "test_name": test_name})

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
        await self.add_results(user.id, test_name, default_results)

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
    # Change detection can be disabled for metrics on a per-user (or per-org),
    # per-test basis.
    #
    # This is useful when certain metrics are too noisy to be useful and users just
    # want to outright not used them.
    #
    # A metric is "disabled" by adding a document to the "metrics" collection. It can
    # be re-enabled by removing the document.
    #
    async def disable_changes(self, id: Any, test_name: str, metrics: List[str]):
        """
        Disable changes for a given user (or org), test, metric combination.
        """
        for metric in metrics:
            await self.db.metrics.insert_one(
                {
                    "user_id": id,
                    "test_name": test_name,
                    "metric_name": metric,
                    "is_disabled": True,
                }
            )

    async def enable_changes(self, id: Any, test_name: str, metrics: List[str]):
        """
        Enable changes for a given user (or org), test, metric combination.
        """
        if not metrics:
            # Enable all metrics
            await self.db.metrics.delete_many(
                {"user_id": id, "test_name": test_name, "is_disabled": True}
            )
        else:
            for metric in metrics:
                await self.db.metrics.delete_one(
                    {
                        "user_id": id,
                        "test_name": test_name,
                        "metric_name": metric,
                        "is_disabled": True,
                    }
                )

    async def get_disabled_metrics(self, id: Any, test_name: str) -> List[str]:
        """
        Get a list of disabled metrics for a given user or org id and test name.

        Returns an empty list if no results are found.
        """
        metrics = self.db.metrics
        return await metrics.distinct(
            "metric_name", {"user_id": id, "test_name": test_name}
        )

    async def get_user_config(self, id: Any):
        """
        Get the user's (or organization) configuration.

        If the user has no configuration, return an empty dictionary.
        """
        exclude_projection = {"_id": 0, "user_id": 0}
        user_config = self.db.user_config
        config = await user_config.find_one({"user_id": id}, exclude_projection)

        return config if config else {}

    async def set_user_config(self, id: Any, config: Dict):
        """
        Set the user's (or organization) configuration.

        We don't do any validation on the configuration, so it's up to the caller to
        ensure that the configuration is valid.
        """
        user_config = self.db.user_config
        await user_config.update_one({"user_id": id}, {"$set": config}, upsert=True)

    async def delete_user_config(self, id: Any):
        """
        Delete the user's (or organization) configuration.

        If the user has no configuration, do nothing.
        """
        user_config = self.db.user_config
        await user_config.delete_one({"user_id": id})

    async def get_test_config(self, id: Any, test_name: str) -> List[Dict]:
        """
        Get the test's configuration.

        If the test has no configuration, return an empty list.
        """
        exclude_projection = {"_id": 0, "test_name": 0, "user_id": 0}
        test_config = self.db.test_config
        config = await test_config.find(
            {"user_id": id, "test_name": test_name}, exclude_projection
        ).to_list(None)

        return config if config else []

    async def set_test_config(self, id: Any, test_name: str, config: List[Dict]):
        """
        Set the test's configuration.

        We don't do any validation on the configuration, so it's up to the caller to
        ensure that the configuration is valid.
        """
        test_config = self.db.test_config

        # Build _id from user_id, test_name, git_repo and branch
        internal_configs = []
        for conf in config:
            c = dict(conf)
            primary_key = OrderedDict(
                {
                    "git_repo": conf["attributes"]["git_repo"],
                    "branch": conf["attributes"]["branch"],
                    "test_name": test_name,
                    "user_id": id,
                }
            )

            c["_id"] = primary_key
            c["user_id"] = id
            c["test_name"] = test_name
            internal_configs.append(c)

        # Perform an upsert
        for c in internal_configs:
            await test_config.update_one({"_id": c["_id"]}, {"$set": c}, upsert=True)

    async def delete_test_config(self, id: Any, test_name: str):
        """
        Delete the test's configuration.

        If the test has no configuration, do nothing.
        """
        test_config = self.db.test_config
        await test_config.delete_many({"user_id": id, "test_name": test_name})

    async def get_public_results(self) -> List[Dict]:
        """
        Get all public results.

        Returns an empty list if no results are found.
        """
        test_configs = self.db.test_config
        exclude_projection = {"_id": 0, "user_id": 0, "public": 0}
        return (
            await test_configs.find({"public": True}, exclude_projection)
            .sort("attributes, test_name")
            .to_list(None)
        )

    async def set_public_map(self, public_test_name, id, is_public):
        """
        Update the public results map. This is a simple mapping from a public test
        name to an id to show which user or organization "owns" the public name.

        This is called when the user sets a test to be public or private.

        If a mapping already exists for a different user, raise a DBStoreResultExists
        """
        public_results = self.db.public_results

        if is_public:
            # Only update if the user is the same
            result = await public_results.find_one({"_id": public_test_name})
            if result and result["user_id"] != id:
                raise DBStoreResultExists(result["user_id"])
            else:
                await public_results.update_one(
                    {"_id": public_test_name},
                    {"$set": {"user_id": id}},
                    upsert=True,
                )
        else:
            # Remove the test from the public results map
            await public_results.delete_one({"_id": public_test_name})

    async def get_public_user(self, public_test_name):
        """
        Get the user who owns the public test name.

        Returns None if no results are found.
        """
        public_results = self.db.public_results
        result = await public_results.find_one({"_id": public_test_name})
        return result["user_id"] if result else None


# Will be patched by conftest.py if we're running tests
_TESTING = False


async def do_on_startup():
    store = DBStore()
    strategy = MockDBStrategy() if _TESTING else MongoDBStrategy()
    store.setup(strategy)
    await store.startup()
