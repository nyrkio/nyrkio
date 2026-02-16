# Copyright (c) 2024, Nyrkiö Oy

from abc import abstractmethod, ABC
from collections import OrderedDict
from datetime import datetime, timezone
import logging
import os
from typing import Dict, List, Tuple, Optional, Any

from bson.objectid import ObjectId
import motor.motor_asyncio
from pymongo.errors import BulkWriteError
import asyncio
from mongomock_motor import AsyncMongoMockClient
from beanie import Document, PydanticObjectId, init_beanie
from fastapi_users.db import BaseOAuthAccount, BeanieBaseUser, BeanieUserDatabase
from fastapi_users import schemas
from pydantic import Field

from hunter.series import AnalyzedSeries


class OAuthAccount(BaseOAuthAccount):
    organizations: Optional[List[Dict]] = Field(default_factory=list)


class User(BeanieBaseUser, Document):
    oauth_accounts: Optional[List[OAuthAccount]] = Field(default_factory=list)
    slack: Optional[Dict[str, Any]] = Field(default_factory=dict)
    billing: Optional[Dict[str, str]] = Field(None)
    billing_runners: Optional[Dict[str, str]] = Field(None)
    superuser: Optional[Dict[str, str]] = Field(None)
    github_username: Optional[str] = Field(None)
    is_cph_user: Optional[bool] = None
    is_repo_owner: Optional[bool] = False


# class BeanieBaseUser(BaseModel):
#     email: str
#     hashed_password: str
#     is_active: bool = True
#     is_superuser: bool = False
#     is_verified: bool = False
#
#     class Settings:
#         email_collation = Collation("en", strength=2)
#         indexes = [
#             IndexModel(
#                 "email",
#                 name="case_insensitive_email_index",
#                 collation=email_collation,
#                 unique=True,
#             ),
#         ]


class NyrkioUserDatabase(BeanieUserDatabase):
    def __init__(self):
        super().__init__(User, OAuthAccount)
        self.store = DBStore()
        self.User = self.store.db.User

    async def get_by_github_username(self, github_username: str):
        res = await self.User.find_one({github_username: github_username})
        if res:
            return User(**res)

        res = await self.User.find(
            {"oauth_accounts.organizations.user.login": github_username}
        ).to_list(99)

        if len(res) == 1:
            obj = res[0]
            return User(**obj)

        if len(res) > 1:
            raise DBStoreMultipleResults(
                f"Failed to get user by their github_username '{github_username}'. Query returned more than one result."
            )

        return None


async def get_user_db():
    # yield BeanieUserDatabase(User, OAuthAccount)
    yield NyrkioUserDatabase()


class UserRead(schemas.BaseUser[PydanticObjectId]):
    oauth_accounts: Optional[List[OAuthAccount]] = Field(default_factory=list)
    slack: Optional[Dict[str, Any]] = Field(default_factory=dict)
    billing: Optional[Dict[str, str]] = Field(None)
    billing_runners: Optional[Dict[str, str]] = Field(None)


class UserCreate(schemas.BaseUserCreate):
    oauth_accounts: Optional[List[OAuthAccount]] = Field(default_factory=list)
    slack: Optional[Dict[str, Any]] = Field(
        default_factory=dict
    )  # Filtered out in backend.common.UserManager.create
    billing: Optional[Dict[str, str]] = Field(
        None
    )  # Filtered out in backend.common.UserManager.create
    billing_runners: Optional[Dict[str, str]] = Field(
        None
    )  # Filtered out in backend.common.UserManager.create
    github_username: Optional[str] = Field(None)
    is_cph_user: Optional[bool] = None
    is_repo_owner: Optional[bool] = False
    # Change the default: Verify your email first, then you're active
    is_active: Optional[bool] = False
    captcha_score: Optional[float] = None
    catcha_provider: Optional[str] = None


class UserUpdate(schemas.BaseUserUpdate):
    oauth_accounts: Optional[List[OAuthAccount]] = Field(default_factory=list)
    slack: Optional[Dict[str, Any]] = Field(default_factory=dict)
    billing: Optional[Dict[str, str]] = Field(None)
    billing_runners: Optional[Dict[str, str]] = Field(None)


class ConnectionStrategy(ABC):
    @abstractmethod
    def connect(self):
        pass

    async def init_db(self):
        pass


NULL_DATETIME = datetime(1970, 1, 1, 0, 0, 0, 0)


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
        asyncio.get_event_loop().set_debug(True)
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

    DEFAULT_DATA = [
        {
            "timestamp": 1,
            "metrics": [
                {
                    "name": "foo",
                    "value": 1.0,
                    "unit": "ms",
                },
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        },
        {
            "timestamp": 2,
            "metrics": [
                {
                    "name": "foo",
                    "value": 1.0,
                    "unit": "ms",
                },
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123457",
            },
        },
        {
            "timestamp": 3,
            "metrics": [
                {
                    "name": "foo",
                    "value": 30.0,
                    "unit": "ms",
                },
            ],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123458",
            },
        },
    ]

    async def init_db(self):
        # Add test users
        from backend.auth.auth import UserManager

        user = UserCreate(
            id=1, email="john@foo.com", password="foo", is_active=True, is_verified=True
        )
        manager = UserManager(BeanieUserDatabase(User, OAuthAccount))
        self.user = await manager.create(user)

        # Add some default data
        results = [
            DBStore.create_doc_with_metadata(r, self.user.id, "default_benchmark")
            for r in self.DEFAULT_DATA
        ]
        await self.connection.default_data.insert_many(results)

        # Usually a new user would get the default data automatically,
        # but since we added the default data after the user was created,
        # we need to add it manually.
        await self.connection.test_results.insert_many(results)

        su = UserCreate(
            id=2,
            email="admin@foo.com",
            password="admin",
            is_active=True,
            is_verified=True,
            is_superuser=True,
        )
        await manager.create(su)

        self.gh_users = []
        gh_user1 = UserCreate(
            id=3,
            email="gh@foo.com",
            password="gh",
            is_active=True,
            is_verified=True,
            github_username="ghuser",
            oauth_accounts=[
                OAuthAccount(
                    account_id="123",
                    account_email="gh@foo.com",
                    oauth_name="github",
                    access_token="gh_token",
                    # Note (Henrik): Top level "login" and "id" used to be there in github responses,
                    # now they no longer are. Felt tedious to update a lot of unit tests to match
                    # reality so instead maintaining a backward compatibility here...
                    organizations=[
                        {
                            "login": "nyrkio",
                            "id": 123,
                            "url": "https://api.github.com/orgs/nyrkio/memberships/foo",
                            "organization_url": "https://api.github.com/orgs/bar",
                            "user": {"login": "ghuser", "id": 3},
                            "organization": {
                                "login": "nyrkio",
                                "id": 123,
                                "url": "https://api.github.com/orgs/nyrkio",
                            },
                        },
                        {
                            "login": "nyrkio2",
                            "id": 456,
                            "url": "https://api.github.com/orgs/nyrkio2/memberships/foo",
                            "organization_url": "https://api.github.com/orgs/bar",
                            "user": {"login": "ghuser", "id": 3},
                            "organization": {
                                "login": "nyrkio2",
                                "id": 456,
                                "url": "https://api.github.com/orgs/nyrkio2",
                            },
                        },
                    ],
                )
            ],
        )
        self.gh_users.append(await manager.create(gh_user1))

        gh_user2 = UserCreate(
            id=4,
            email="gh2@foo.com",
            password="gh",
            is_active=True,
            is_verified=True,
            github_username="ghuser2",
            oauth_accounts=[
                OAuthAccount(
                    account_id="456",
                    account_email="gh2@foo.com",
                    oauth_name="github",
                    access_token="gh_token",
                    organizations=[
                        {"login": "nyrkio2", "id": 456},
                        {"login": "nyrkio3", "id": 789},
                    ],
                )
            ],
        )
        self.gh_users.append(await manager.create(gh_user2))

    def get_test_user(self):
        assert self.user, "init_db() must be called first"
        return self.user

    def get_github_users(self):
        assert self.gh_users, "init_db() must be called first"
        return self.gh_users


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


class DBStoreMultipleResults(Exception):
    """
    Raised when a single record is expected or at least desired, and DB returning multiple leads to ambiguity.
    """

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
    def check_for_missing_keys(data):
        """
        This function is responsible for validating the incoming JSON data and
        checking that it conforms to our schema.
        """

        missing_keys = []

        # Make sure all the required keys are present
        for key in ["timestamp", "attributes"]:
            if key not in data:
                missing_keys.append(key)

        attr_keys = ("git_repo", "branch", "git_commit")
        if "attributes" not in data:
            # They're all missing
            missing_keys.extend([f"attributes.{k}" for k in attr_keys])
            missing_keys.append(missing_keys)
        else:
            for key in attr_keys:
                if key not in data["attributes"]:
                    missing_keys.append(f"attributes.{key}")

        metric_keys = ("name", "value", "unit")
        if "metrics" not in data:
            # they're all missing
            missing_keys.extend([f"metrics.{k}" for k in metric_keys])
            missing_keys.append(missing_keys)
        else:
            for key in metric_keys:
                for metric in data["metrics"]:
                    if key not in metric:
                        missing_keys.append(f"metrics.{key}")

        return missing_keys

    @staticmethod
    def _force_uri_format(uri):
        """
        Force git_repo to be of a specific format

        As git_repo is used as a primary key and in any case for querying, we have to
        force some stricter rules than what HTTP and browsers allow for URIs.

         - Remove trailing slash: https://github.com/org/repo/ -> https://github.com/org/repo/
         - all lowercase
        """
        if uri.endswith("/"):
            uri = uri[:-1]

        uri = uri.lower()

        return uri

    @staticmethod
    def create_doc_with_metadata(
        doc: Dict, id: Any, test_name: str, pull_number=None
    ) -> Dict:
        """
        Return a new document with added metadata, e.g. the version of the schema and the user ID.

        This is used when storing documents in the DB.

          id -> The ID of the user who created the document. Can also be a GitHub org ID
          version -> The version of the schema for the document
          test_name -> The name of the test
          last_modified -> UTC timestamp. Used to reference a specific Series matched with pre-computed change points.

        We also build a primary key from the git_repo, branch, git_commit,
        test_name, timestamp, and user ID. If any of the keys are missing,
        raise a DBStoreMissingKeys exception.
        """
        d = dict(doc)

        missing_keys = DBStore.check_for_missing_keys(d)
        if len(missing_keys) > 0:
            raise DBStoreMissingRequiredKeys(missing_keys)
        d["attributes"]["git_repo"] = DBStore._force_uri_format(
            d["attributes"]["git_repo"]
        )

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
        d["meta"] = {"last_modified": datetime.now(tz=timezone.utc)}
        if pull_number:
            d["pull_request"] = pull_number

        return d

    async def add_results(
        self,
        id: Any,
        test_name: str,
        results: List[Dict],
        update: bool = False,
        pull_number=None,
    ):
        """
        Create the representation of test results for storing in the DB, e.g. add
        metadata like user id and version of the schema.

        If the user tries to add a result that already exists (and update is
        False), raise a DBStoreResultExists exception. Otherwise, update the
        existing result.
        """
        if isinstance(id, str):
            id = ObjectId(id)

        new_list = [
            DBStore.create_doc_with_metadata(r, id, test_name, pull_number)
            for r in results
        ]
        test_results = self.db.test_results

        if update:
            for r in new_list:
                await test_results.update_one(
                    {"_id": r["_id"]}, {"$set": r}, upsert=True
                )
        else:
            try:
                await test_results.insert_many(new_list)
            except BulkWriteError as e:
                if e.details["writeErrors"][0]["code"] == 11000:
                    duplicate_key = e.details["writeErrors"][0]["op"]["_id"]

                    # Don't leak user_id to the client. Anyway, it's not JSON
                    # serializable.
                    del duplicate_key["user_id"]

                    raise DBStoreResultExists(duplicate_key)

    async def get_results(
        self, id: Any, test_name: str, pull_request=None, pr_commit=None
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        Retrieve test results for a given user and test name. The results are
        guaranteed to be sorted by timestamp in ascending order.

        If no results are found, return (None,None).

        If pull_request and pr_commit are not None, then return results where
        the pull_request field is empty or matches the pull_request and
        pr_commit arguments. This is used to filter results so you get A) the
        historic results of a branch (e.g. main) and B) the pull request
        result for the exact pr_commit.
        """
        test_results = self.db.test_results

        # Strip out the internal keys
        exclude_projection = {key: 0 for key in self._internal_keys}

        # if test_name is None:
        #     # Should always be true in our case
        #     test_name = {"$lt":-999}
        if isinstance(id, str):
            id = ObjectId(id)
        query = {
            "user_id": id,
            "test_name": test_name,
            "pull_request": {"$exists": False},
        }

        # print(query)
        if pull_request:
            pull_query = {
                "test_name": test_name,
                "pull_request": pull_request,
            }
            # print(pr_commit, type(pr_commit))
            # We foolishly have allowed API endpoint where you don't provide pr_commit
            # Returning lots of commits pushed to the same PR doesn't make sense. We'll
            # sort by timestamp and return the latest one.
            # To avoid ambiguity, always provide the commit sha
            if pr_commit:
                pull_query["attributes.git_commit"] = pr_commit

            # print(pull_query)
            # New strategy: Just get the pr first. This could be a graphLookup query but this is easy to follow.
            pr_result = (
                await test_results.find(pull_query, exclude_projection)
                .sort("timestamp", -1)
                .to_list(None)
            )
            # print(pr_result)
            if len(pr_result) == 0:
                return [], []
            pr_result = pr_result[0]

            # we want to compare the pr result to its history.
            # if there are results that are newer than the PR base commit, ignore those
            base_timestamp = None
            if (
                "extra_info" in pr_result
                and pr_result["extra_info"] is not None
                and "base_commit" in pr_result["extra_info"]
            ):
                base_timestamp = pr_result["extra_info"]["base_commit"].get("timestamp")
            pr_timestamp = pr_result.get("timestamp")
            if base_timestamp is not None:
                query["timestamp"] = {"$lte": base_timestamp}
            elif pr_timestamp is not None:
                # Don't have info about base commit, but just take the commits that are older than the pr commit.
                query["timestamp"] = {"$lte": pr_timestamp}
            else:
                # Just fetch all results for this test_name
                pass

            results = (
                await test_results.find(query, exclude_projection)
                .sort("timestamp")
                .to_list(None)
            )
            # It's valid to rerun the test multiple times and report against the same commit
            results.append(pr_result)

            # if not pr_commit:
            # logging.error(f"pr_commit is None for pull request {pull_request}.")
            # if len(results) > 0:
            #     logging.info("Defaulting to last result.")
            #     pr_commit = list(filter(lambda x: "pull_request" in x, results))[
            #         -1
            #     ]["attributes"]["git_commit"]

            if pr_commit is not None:
                results = filter_out_pr_results(results, pr_commit)
                # print(results)
        else:
            results = (
                await test_results.find(
                    {
                        "user_id": id,
                        "test_name": test_name,
                        "pull_request": {"$exists": False},
                    },
                    exclude_projection,
                )
                .sort("timestamp")
                .to_list(None)
            )
        # print(results)
        return separate_meta(results)

    async def get_test_names(self, id: Any = None, test_name_prefix: str = None) -> Any:
        """
        Get a list of all test names for a given user. If id is None then
        return a dictionary of all test names for all users. Entries are returned
        in sorted order.

        If test_name_prefix is specified, returns the subset of names (paths, really) where the
        beginning of the test name matches the test_name_prefix.

        Returns an empty list if no results are found.
        """
        test_results = self.db.test_results
        if id:
            results = await test_results.aggregate(
                [
                    {"$match": {"user_id": id}},
                    {"$group": {"_id": 0, "test_names": {"$addToSet": "$test_name"}}},
                    {"$sort": {"test_names": 1}},
                ],
            ).to_list(None)
            # TODO(mfleming) Not sure why the mongo query doesn't return sorted results
            # Henrik: Should now but left this anyway as it also modified structure...
            sorted_list = results[0]["test_names"] if results else []
            sorted_list.sort()
            return sorted_list
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

    async def get_all_users(
        self, is_superuser=None, is_active=None, is_verified=None
    ) -> Any:
        User = self.db.User
        query_filter = {}
        fields = {
            "_id": True,
            "email": True,
            "is_active": True,
            "is_superuser": True,
            "is_verified": True,
        }
        if is_superuser is not None:
            filter["is_superuser"] = bool(is_superuser)
        if is_active is not None:
            filter["is_active"] = bool(is_active)
        if is_verified is not None:
            filter["is_verified"] = bool(is_verified)

        results = await User.find(query_filter, fields).to_list(None)
        for result in results:
            result["_id"] = str(result["_id"])
        return results

    async def get_impersonate_user(self, admin_user: str):
        query = {"_id": admin_user, "expire": {"$gt": datetime.now(timezone.utc)}}
        impersonate_mapping = await self.db.impersonate.find_one(query)
        return impersonate_mapping.get("user_id") if impersonate_mapping else None

    async def set_impersonate_user(
        self, admin_user: str, impersonate_user: str, expire: datetime
    ):
        id_doc = {"_id": admin_user.email}
        impersonate_user = {
            "_id": admin_user.email,
            "user_email": impersonate_user.email,
            "user_id": impersonate_user.id,
            "expire": expire,
        }
        await self.db.impersonate.replace_one(id_doc, impersonate_user, upsert=True)

    async def delete_impersonate_user(self, admin_user):
        await self.db.impersonate.delete_many({"_id": admin_user})

    async def delete_all_results(self, user: User):
        """
        Delete all results for a given user.

        If no results are found, do nothing.
        """
        test_results = self.db.test_results
        await test_results.delete_many({"user_id": user.id})

    async def delete_result(
        self, id: Any, test_name: str, timestamp=None, pull_request=None
    ):
        """
        Delete a single result for a given user and test name.

        The semantics of this function are a little weird since we have
        a single function to handle multiple scenarios.

        For regular results (non-pull request), if timestamp is specified,
        delete the result with that timestamp. Instead, if a pull_request is
        specified, delete all results for that pull request. If neither
        timestamp nor pull_request are specified, delete all results for the
        given user and test name.

        This means that you can't delete a pull request result by timestamp.

        If no matching results are found, do nothing.
        """
        test_results = self.db.test_results
        if timestamp:
            await test_results.delete_one(
                {"user_id": id, "test_name": test_name, "timestamp": timestamp}
            )
        elif pull_request:
            await test_results.delete_many(
                {"user_id": id, "test_name": test_name, "pull_request": pull_request}
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

    async def get_default_test_names(self) -> List[str]:
        """
        Get a list of all test names for the default data.

        Returns an empty list if no results are found.
        """
        default_data = self.db.default_data
        return await default_data.distinct("test_name")

    async def get_default_data(self, test_name) -> Tuple[List[Dict], List[Dict]]:
        """
        Get the default data for a new user.
        """
        # Strip out the internal keys
        exclude_projection = {key: 0 for key in self._internal_keys}

        # TODO(matt) We should read results in batches, not all at once
        default_data = self.db.default_data
        cursor = default_data.find({"test_name": test_name}, exclude_projection)
        return separate_meta(await cursor.sort("timestamp").to_list(None))

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

    async def get_user_config(self, user_id: Any) -> Tuple[Dict, Dict]:
        """
        Get the user's (or organization) configuration.

        If the user has no configuration, return an empty dictionary.
        """
        exclude_projection = {"_id": 0, "user_id": 0}
        user_config = self.db.user_config
        config = await user_config.find_one({"user_id": user_id}, exclude_projection)
        if config:
            return separate_meta_one(config)
        else:
            return {}, {}

    async def set_user_config(self, id: Any, config: Dict):
        """
        Set the user's (or organization) configuration.

        We don't do any validation on the configuration, so it's up to the caller to
        ensure that the configuration is valid.

        Note that the incoming config object in many cases will default to None for the fields
        that user didn't set to any value. Hence None means such values should be ignored.
        That again means that once set, a config option cannot be unset. But note that there's
        a HTTP DELETE endpoint that will delete the entire config.
        """
        user_config = self.db.user_config
        editable = dict(config)
        keys = list(editable.keys())
        for k in keys:
            if editable[k] is None:
                del editable[k]
        editable["meta"] = {"last_modified": datetime.now(tz=timezone.utc)}
        await user_config.update_one({"user_id": id}, {"$set": editable}, upsert=True)

    async def delete_user_config(self, id: Any):
        """
        Delete the user's (or organization) configuration.

        If the user has no configuration, do nothing.
        """
        user_config = self.db.user_config
        await user_config.delete_one({"user_id": id})

    async def get_test_config(
        self, id: Any, test_name: str
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        Get the test's configuration.

        If the test has no configuration, return (None,None).
        """
        exclude_projection = {"_id": 0, "test_name": 0, "user_id": 0}
        test_config = self.db.test_config
        config = await test_config.find(
            {"user_id": id, "test_name": test_name}, exclude_projection
        ).to_list(None)

        return separate_meta(config)

    async def set_test_config(self, id: Any, test_name: str, config: List[Dict]):
        """
        Set the test's configuration.

        We don't do any validation on the configuration, so it's up to the
        caller to ensure that the configuration is valid. In particular, we
        don't check whether two public tests conflict.
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
            c["meta"] = {"last_modified": datetime.now(tz=timezone.utc)}
            internal_configs.append(c)

        print("set_test_config()", {"_id": c["_id"]}, c)
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

    async def get_public_results(
        self, user_or_org_id=None
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        Get all public results.

        If user_or_org_id is given, return all public tests owned by that user.

        Returns an empty list if no results are found.
        """
        test_configs = self.db.test_config
        exclude_projection = {"_id": 0}
        query = {"public": True}
        if user_or_org_id is not None:
            if not isinstance(user_or_org_id, int):
                query["user_id"] = ObjectId(user_or_org_id)
            else:
                query["user_id"] = user_or_org_id

        results = (
            await test_configs.find(query, exclude_projection)
            .sort("attributes, test_name")
            .to_list(None)
        )
        return separate_meta(results)

    async def persist_change_points(
        self,
        change_points: Dict[str, AnalyzedSeries],
        id: str,
        series_id_tuple: Tuple[str, float, float, Any],
    ):
        change_points_json = {}
        cp_timestamps = [datetime.now(tz=timezone.utc)]
        for metric_name, analyzed_series in change_points.items():
            if not analyzed_series.test_name() == series_id_tuple[0]:
                print(
                    analyzed_series.test_name()
                    + " must be equal to "
                    + series_id_tuple[0]
                    + " but wasn't!"
                )
            change_points_json[metric_name] = analyzed_series.to_json()
            cp_timestamps.append(analyzed_series.change_points_timestamp)

        primary_key = OrderedDict(
            {
                "user_id": id,
                "test_name": series_id_tuple[0],
                "max_pvalue": series_id_tuple[1],
                "min_magnitude": series_id_tuple[2],
            }
        )
        series_last_modified = series_id_tuple[3]
        change_points_timestamp = min(cp_timestamps)
        doc = {
            "_id": primary_key,
            "meta": {
                "last_modified": series_last_modified,
                "change_points_timestamp": change_points_timestamp,
                # 3 = hunter from_json() includes weak_change_points, w
                # 4 = metrics stores a Metrics object, in particular direction.
                "schema_version": 4,
            },
            "change_points": change_points_json,
        }

        collection = self.db.change_points
        await collection.update_one({"_id": primary_key}, {"$set": doc}, upsert=True)

    async def get_cached_change_points(
        self, user_id: str, series_id_tuple: Tuple[str, float, float, Any]
    ) -> Dict:
        """
        Get the change points for a given user id and test name from the cache.

        Return a dict of change points (key'd by metric name) if they exist.
        If no change points are found, return an empty dict.

        Callers of this function need to handle change point invalidation, i.e.
        recompute the change points for this series. Change points need to be
        invalidated if:

          1. The series has been updated since the change points were computed
          2. The user has updated their config since the change points were computed

        If change points need to be recomputed, return an empty dict.
        """
        results = await self._get_cached_cp_db(
            user_id, series_id_tuple[0], series_id_tuple[1], series_id_tuple[2]
        )
        if results is None:
            return None
        return await self._validate_cached_cp(user_id, results, series_id_tuple[3])

    async def _get_cached_cp_db(
        self, user_id: str, test_name: str, max_pvalue: str, min_magnitude: str
    ) -> Dict:
        collection = self.db.change_points

        search_key = OrderedDict(
            {
                "_id.user_id": user_id,
                "_id.test_name": test_name,
                "_id.max_pvalue": max_pvalue,
                "_id.min_magnitude": min_magnitude,
            }
        )
        # print(search_key)
        results = await collection.find(search_key).to_list(None)
        # print(str(results)[:200])
        if len(results) == 0:
            # Nothing was cached
            return None

        if len(results) != 1:
            # This should never happen. If it does, we can't trust the cache so
            # force a recompute.
            logging.error(
                f"Multiple change points found for {test_name}. Forcing recompute."
            )
            return None

        return results[0]

    def _validate_cached_cp_timestamp(self, meta):
        if not meta:
            # Series doesn't have a last_modified field. It probably predates the time we even
            # had caching for change points.
            # Caller needs to compute the change_points now.
            return False
        if "change_points_timestamp" not in meta:
            # v2, see above
            return False

        return meta["change_points_timestamp"]

    async def _validate_cached_cp(self, user_id, db_results, series_last_modified):
        data, meta = separate_meta_one(db_results)
        change_points_timestamp = self._validate_cached_cp_timestamp(meta)
        if not change_points_timestamp:
            return None

        if change_points_timestamp < series_last_modified:
            # User has updated the series since the change points were last computed.
            # Caller needs to recompute the change points.
            return None

        user_config, user_meta = await self.get_user_config(user_id)
        if not user_config:
            # User has no config, so cannot have invalidated the cache
            return data["change_points"]

        if user_meta and meta["change_points_timestamp"] < user_meta["last_modified"]:
            # User has updated their config since the change points were last computed.
            # Caller needs to recompute the change points.
            return None

        return data["change_points"]

    async def add_pr_test_name(
        self, user_id: Any, repo: str, git_commit: str, pull_number: int, test_name: str
    ):
        """
        Add a list of test_names for a given pull request and git commit.

        Because the pull request API only allows results for a single test name
        to be added at a time, we may need to update the existing list of test
        names for a given pull request and git commit.
        """
        pr_tests = self.db.pr_tests
        id = OrderedDict(
            {
                "git_commit": git_commit,
                "pull_number": pull_number,
                "user_id": user_id,
                "git_repo": repo,
            }
        )

        # Push a new test name onto the list
        await pr_tests.update_one(
            {"_id": id},
            {
                "$push": {"test_names": test_name},
                "$set": {
                    "user_id": user_id,
                    "git_commit": git_commit,
                    "pull_number": pull_number,
                    "git_repo": repo,
                },
            },
            upsert=True,
        )

    async def get_pull_requests_from_the_source(
        self,
        user_id=None,
        repo=None,
        git_commit=None,
        pull_number=None,
        branch=None,
        test_names=None,
    ) -> List[Dict]:
        """
        Get a list of pull requests for a given user.

        If any of repo, git_commit, or pull_number are None, return all pull
        requests for the user. Otherwise, return the pull request that matches
        the given repo, git_commit, and pull_number. Note that in the latter
        case, is user_id is None, return pull requests for all users submitted
        against the repo. (e.g. random contributors to an open source project
        will all have different user_id, but all submitted valid PRs against the repo.)

        Each entry in the list is a dict with the following keys:
          - git_repo - the git repository
          - git_commit - the git commit
          - pull_number - the pull request number
          - test_names - a list of test names

        NOTE: git_repo should not include the protocol or github.com domain.

        Return an empty list if no results are found.
        """
        if (
            repo is not None
            and not repo.startswith("https://github.com/")
            and not repo.startswith("https:/github.com/")
        ):
            repo = f"https://github.com/{repo}"

        coll = self.db.test_results

        query = {"pull_request": {"$exists": 1}}
        if user_id is not None:
            if not isinstance(user_id, int):
                query["user_id"] = ObjectId(user_id)
            else:
                query["user_id"] = user_id
        if repo:
            query["attributes.git_repo"] = repo
        if branch:
            query["attributes.branch"] = branch
        if test_names is not None:
            query["test_name"] = {"$in": test_names}
        if pull_number:
            query["pull_request"] = pull_number
        if git_commit:
            query["attributes.git_commit"] = git_commit

        # print(query)
        pipeline = [
            {"$match": query},
            {
                "$group": {
                    "_id": {
                        "git_repo": "$attributes.git_repo",
                        "branch": "$attributes.branch",
                        "git_commit": "$attributes.git_commit",
                        "pull_request": "$pull_request",
                    },
                    "test_names": {"$addToSet": "$test_name"},
                }
            },
            {
                "$project": {
                    "_id": False,
                    "git_repo": "$_id.git_repo",
                    "branch": "$_id.branch",
                    "git_commit": "$_id.git_commit",
                    "pull_number": "$_id.pull_request",
                    "test_names": "$test_names",
                }
            },
            {"$sort": {"pull_number": -1}},
        ]
        # {"$limit": 50},
        # print(pipeline)
        pulls = await coll.aggregate(pipeline).to_list(None)
        # print(pulls)
        return pulls

    async def get_pull_requests(
        self,
        user_id=None,
        repo=None,
        git_commit=None,
        pull_number=None,
        branch=None,
        test_names=None,
    ) -> List[Dict]:
        """
        Get a list of pull requests for a given user.

        If any of repo, git_commit, or pull_number are None, return all pull
        requests for the user. Otherwise, return the pull request that matches
        the given repo, git_commit, and pull_number. Note that in the latter
        case, is user_id is None, return pull requests for all users submitted
        against the repo. (e.g. random contributors to an open source project
        will all have different user_id, but all submitted valid PRs against the repo.)

        Each entry in the list is a dict with the following keys:
          - git_repo - the git repository
          - git_commit - the git commit
          - pull_number - the pull request number
          - test_names - a list of test names

        NOTE: git_repo should not include the protocol or github.com domain.

        Return an empty list if no results are found.
        """
        if test_names is None:
            test_names = []

        pr_tests = self.db.pr_tests
        if user_id is not None:
            # Do a lookup on the primary key if we have all the fields
            if repo and git_commit and pull_number:
                primary_key = OrderedDict(
                    {
                        "git_commit": git_commit,
                        "pull_number": pull_number,
                        "user_id": user_id,
                        "git_repo": repo,
                    }
                )
                test_names = await pr_tests.find_one({"_id": primary_key})
                return build_pulls([test_names]) if test_names else []

            # Otherwise, do a lookup on the user_id and any other attributes
            query = {"user_id": user_id}
            if repo:
                query["git_repo"] = repo
            if branch:
                query["branch"] = branch
            if test_names:
                query["test_name"] = {"$in": test_names}

            pulls = (
                await pr_tests.find(query)
                .sort("pull_number", -1)
                .limit(50)
                .to_list(None)
            )
            return build_pulls(pulls)

        # Then again, is user_id is None, get PRs just based on the repo
        if repo is not None:
            query = {"git_repo": repo}
            if branch:
                query["branch"] = branch
            if test_names:
                query["test_name"] = {"$in": test_names}

            pulls = (
                await pr_tests.find(query)
                .sort("pull_number", -1)
                .limit(50)
                .to_list(None)
            )
            return build_pulls(pulls)

    async def delete_pull_requests(self, user_id: Any, repo: str, pull_number: int):
        """
        Delete a pull request for a given user.
        """
        pr_tests = self.db.pr_tests
        await pr_tests.delete_many(
            {
                "user_id": user_id,
                "pull_number": pull_number,
                "git_repo": repo,
            }
        )

    async def get_user_without_any_fastapi_nonsense(self, user_id):
        # Note that using pydantic models with MongoDB results in the user id quickly becoming a string
        # We must recreate the MongoDB ObjectId here so queries match what's actually in the database
        users_collection = self.db.User
        db_user_id = user_id
        if not isinstance(user_id, ObjectId):
            if isinstance(user_id, str):
                db_user_id = ObjectId(user_id)
            else:
                raise ValueError(
                    f"user_id must be a str or ObjectId ({user_id} is {type(user_id)})"
                )

        logging.debug(db_user_id)
        logging.debug(type(db_user_id))
        return await users_collection.find_one({"_id": db_user_id})

    async def list_users(self):
        users_collection = self.db.User
        query: Dict[str, Any] = {"is_active": True}
        cursor = users_collection.find(query)

        results = [
            User(**obj) async for obj in cursor
        ]  # For each result, MongoDB gives us a raw dictionary that we hydrate back in our Pydantic model

        return results

    async def list_orgs(self):
        users_collection = self.db.User
        agg_query: List[Dict] = [
            {"$unwind": {"path": "$oauth_accounts"}},
            {"$unwind": {"path": "$oauth_accounts.organizations"}},
            {
                "$group": {
                    "_id": "$oauth_accounts.organizations.organization.id",
                    "org_name": {
                        "$addToSet": "$oauth_accounts.organizations.organization.login"
                    },
                    "org_url": {
                        "$addToSet": "$oauth_accounts.organizations.organization.url"
                    },
                }
            },
            {
                "$group": {
                    "_id": 1,
                    "all_orgs_id": {"$push": "$_id"},
                    "all_orgs_name": {"$push": "$org_name"},
                }
            },
        ]
        results = await users_collection.aggregate(agg_query).to_list(None)
        if results:
            return results[0]["all_orgs_id"]
        else:
            return []

    async def get_summaries_cache(self, user_id):
        coll = self.db.summaries_cache
        results = await coll.find({"_id": user_id}).to_list(None)
        if results is None or len(results) == 0:
            return {}
        cache2 = results[0]
        cache1 = {}
        for k, v in cache2.items():
            if k == "_id":
                continue

            k1 = k
            k1 = k1.replace("¤", ".")
            cache1[k1] = cache2[k]

        return cache1

    async def save_summaries_cache(self, user_id, cache):
        cache["_id"] = user_id
        cache2 = {}
        for k, v in cache.items():
            k2 = k
            k2 = k2.replace(".", "¤")
            cache2[k2] = cache[k]
        self.db.summaries_cache.update_one(
            {"_id": user_id}, {"$set": cache2}, upsert=True
        )

    async def log_json_event(self, json_event, event_type="default"):
        coll = self.db.event_log
        wrapper = {
            "event_type": event_type,
            "nyrkio_datetime": datetime.now(tz=timezone.utc),
            "json_event": json_event,
        }
        await coll.insert_one(wrapper)

    async def get_reported_commits(self, user_or_org_id):
        coll = self.db.reported_commits
        query = {}
        if not isinstance(user_or_org_id, int):
            query["user_id"] = ObjectId(user_or_org_id)
        else:
            query["user_id"] = user_or_org_id

        return await coll.find_one(query)

    async def save_reported_commits(self, reported_commits, user_or_org_id):
        coll = self.db.reported_commits
        query = {}
        if not isinstance(user_or_org_id, int):
            query["user_id"] = ObjectId(user_or_org_id)
        else:
            query["user_id"] = user_or_org_id
        if not isinstance(reported_commits, dict):
            raise ValueError("reported_commits must be a dictionary {}")
        return await coll.update_one(query, {"$set": reported_commits}, upsert=True)

    async def list_github_installations(self):
        coll = self.db.github_installations
        return await coll.find().to_list(None)

    async def set_github_installation(self, gh_id, gh_event):
        coll = self.db.github_installations
        return await coll.update_one(
            {"_id": int(gh_id)}, {"$set": gh_event}, upsert=True
        )

    async def get_github_installation(self, gh_id):
        coll = self.db.github_installations
        return await coll.find_one({"_id": int(gh_id)})

    async def get_user_by_github_username(self, github_username: str):
        print("get_user_by_github_username")
        res = await self.db.User.find_one({"github_username": github_username})
        if res:
            print("get_user_by_github_username 2")
            return User(**res)

        print("get_user_by_github_username 3")
        res = await self.db.User.find(
            {"oauth_accounts.organizations.user.login": github_username}
        ).to_list(99)

        if len(res) == 1:
            print("get_user_by_github_username 4")
            obj = res[0]
            return User(**obj)

        print("get_user_by_github_username 5")
        if len(res) > 1:
            raise DBStoreMultipleResults(
                f"Failed to get user by their github_username '{github_username}'. Query returned more than one result."
            )

        return None

    async def get_org_by_github_org(self, github_org: str, github_username: str = None):
        print(f"get_org_by_github_org {github_org} {github_username}")
        query = {"oauth_accounts.organizations.organization.login": github_org}
        if github_username:
            query["oauth_accounts.organizations.user.login"] = github_username
        res = await self.db.User.find(query).to_list(99)

        if len(res) == 1:
            print("get_org_by_github_org 4")
            for oauth in res[0]["oauth_accounts"]:
                for org in oauth["organizations"]:
                    if org["organization"]["login"] == github_org:
                        return org

        print("get_org_by_github_org 5")
        if len(res) > 1:
            # This is not good but actually they can all be the same github_org
            orgs = {}
            for one_org in res:
                for oauth in one_org["oauth_accounts"]:
                    for org in oauth["organizations"]:
                        if org["organization"]["login"] == github_org:
                            orgs[org["organization"]["id"]] = org

            if len(list(orgs.keys())) == 1:
                return list(orgs.values())[0]
            else:
                raise DBStoreMultipleResults(
                    f"Failed to get a nyrkio org from github_org '{github_org}' (user={github_username}). Query returned more than one result."
                )

        return None

    async def queue_work_task(self, event, task_type="default"):
        coll = self.db.work_queue
        wrapper = {
            "task_type": task_type,
            "nyrkio_datetime": datetime.now(tz=timezone.utc).timestamp(),
            "task": event,
            "status": "queued",
        }
        await coll.insert_one(wrapper)
        if task_type in ["workflow_job"]:
            runid = event[task_type]["run_id"]
            logging.info(f"Work task {runid} added to queue")
        else:
            d = wrapper["nyrkio_datetime"]
            logging.info(f"Work tast {task_type}/{d} added to queue")

    async def check_work_queue(self, task_type="default"):
        await self.timeout_tasks(task_type)
        coll = self.db.work_queue
        q = {
            "task_type": task_type,
            "status": "queued",
        }
        task = await coll.find_one_and_update(
            q, {"$set": {"status": "working"}}, sort=[("nyrkio_datetime", 1)]
        )
        logging.info(f"Found task {task} in the queue")
        if task:
            # Note: Unusually return the document with the _id field.
            # This is so that we can mark it done or delete later.
            return task

        return None

    async def timeout_tasks(self, task_type="default", hours_ago=2):
        time_ago = ((datetime.now(tz=timezone.utc).timestamp() - hours_ago * 60 * 60),)
        coll = self.db.work_queue
        q = {
            "task_type": task_type,
            "status": "working",
            "nyrkio_datetime": {"$lt": time_ago},
            "reset_counter": {"$lt": 5},
        }
        not_completed_tasks = (
            await coll.find(q).sort("nyrkio_datetime", 1).limit(100).to_list(None)
        )
        if not_completed_tasks:
            logging.warning(
                "The following tasks in the work queue are {hours_ago} old. Resetting."
            )
            logging.warning(not_completed_tasks)
            for t in not_completed_tasks:
                await coll.find_one_and_update(
                    {"_id": t["_id"]},
                    {"$set": {"status": "queued"}, "$inc": {"reset_counter"}},
                )

    async def work_task_done(self, task):
        coll = self.db.work_queue
        q = {"_id": task["_id"]}
        now = datetime.now(tz=timezone.utc).timestamp()
        result = await coll.update_one(
            q, {"$set": {"status": "done", "nyrkio_done": now}}
        )
        print("done", result)

    async def get_sso_config(
        self, oauth_full_domain=None, oauth_issuer=None, org_domain=None
    ):
        coll = self.db.sso
        q = {}
        if oauth_full_domain is not None:
            q["oauth_full_domain"] = oauth_full_domain
        if oauth_issuer is not None:
            q["oauth_issuer"] = oauth_issuer
        if org_domain is not None:
            q["org_domain"] = org_domain
        results = await coll.find(q).to_list(None)
        print(q, results)
        return results

    async def get_pat(self, user_id):
        coll = self.db.User
        u = await coll.find_one({"_id": user_id})
        print(type(u))
        if isinstance(u, dict):
            return u.get("github_pat")
        return

    async def set_pat(self, user_id, pat):
        coll = self.db.User
        await coll.update_one({"_id": user_id}, {"github_pat": {"$set": pat}})

    async def get_monthly_runner_cpu_hours(self, plan: str, billable_user_id: str):
        """
        Get total CPU-hours consumed this calendar month for a given billable user/org.
        Queries runner_usage_raw aggregated by user.billable_nyrkio_user_id.
        """
        now = datetime.now(tz=timezone.utc)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_start_iso = month_start.isoformat()

        coll = self.db.runner_usage_raw
        pipeline = [
            {
                "$match": {
                    "user.billable_nyrkio_user_id": str(billable_user_id),
                    "plan_info.plan": str(plan),
                    "unique_key.unique_time_slot": {"$gte": month_start_iso},
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_cpu_hours": {"$sum": "$consumption.nyrkio_cpu_hours"},
                    "max_timestamp": {"$max": "$unique_key.unique_time_slot"},
                }
            },
        ]
        results = await coll.aggregate(pipeline).to_list(None)
        if not results:
            return 0.0, now

        cpuh = results[0]["total_cpu_hours"]
        t = results[0]["max_timestamp"]
        t = t.split("Z-")[0]  # TODO: python 3.11 supports Z
        t = datetime.fromisoformat(t)

        return cpuh, t

    async def get_latest_runner_report(self):
        coll = self.db.runner_usage_latest_report
        res = await coll.find_one({"_id": "latest_usage_report"})
        if res:
            return res["key"]
        return None

    async def set_latest_runner_report(self, key):
        coll = self.db.runner_usage_latest_report
        await coll.update_one(
            {"_id": "latest_usage_report"}, {"$set": {"key": key}}, upsert=True
        )

    async def add_user_runner_usage(self, user_id, user_runner_usage, report_key=None):
        coll = self.db.runner_usage
        await coll.insert_one(
            {
                "user_id": user_id,
                "runner_usage": user_runner_usage,
                "report": report_key,
                "nyrkio_datetime": datetime.now(tz=timezone.utc),
            }
        )

    async def add_user_runner_usage_raw(self, user_runner_usage):
        if user_runner_usage:
            coll = self.db.runner_usage_raw
            await coll.insert_many(user_runner_usage)

    async def add_reported_stripe_id(self, unique_stripe_id):
        if isinstance(unique_stripe_id, str) and unique_stripe_id != "":
            unique_stripe_id = [unique_stripe_id]
        if not isinstance(unique_stripe_id, list):
            raise ValueError(
                "The incoming data must be either a nonempty string, or list of strings."
            )
        if unique_stripe_id:
            docs = [{"_id": id_string} for id_string in unique_stripe_id]
            coll = self.db.runner_usage_reported_to_stripe
            await coll.insert_many(docs, ordered=False)

    async def check_new_stripe_ids(self, unique_stripe_id):
        if isinstance(unique_stripe_id, str) and unique_stripe_id != "":
            unique_stripe_id = [unique_stripe_id]
        if not isinstance(unique_stripe_id, list):
            raise ValueError(
                "The incoming data must be either a nonempty string, or list of strings."
            )
        query = {"_id": {"$in": unique_stripe_id}}
        coll = self.db.runner_usage_reported_to_stripe
        res = await coll.find(query).to_list(None)
        reported_docs = [doc["_id"] for doc in res]
        new_docs = [idd for idd in unique_stripe_id if idd not in reported_docs]
        return new_docs


# Will be patched by conftest.py if we're running tests
_TESTING = False


async def do_on_startup():
    store = DBStore()
    strategy = MockDBStrategy() if _TESTING else MongoDBStrategy()
    store.setup(strategy)
    await store.startup()


def separate_meta_one(doc: Dict) -> Tuple[Dict, Dict]:
    """
    Split user data and metadata fields and return both.

    The metadata part contains fields that shouldn't be returned outside the
    HTTP API. (api.py)

    If no metadata is found (because this is an old document that was written
    before we appended metadata in add_results()), the second tuple element
    will be an empty dict.
    """
    dup = dict(doc)
    meta = {}

    if "meta" in dup:
        meta = dup["meta"]
        del dup["meta"]

    return dup, meta


def separate_meta(doc: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    """
    Split user data and metadata fields and return both.

    Returns two lists, one with the data and one with the metadata. Each entry
    in the list is a dict and both lists have the same number of elements.
    """
    data = []
    metadata = []
    for d in doc:
        dup, meta = separate_meta_one(d)
        data.append(dup)
        metadata.append(meta)

    return data, metadata


def build_pulls(pr_tests_result):
    """Convert the PR tests result to the "pulls" format."""
    results = []
    for pr in pr_tests_result:
        pulls = {
            "git_repo": pr["git_repo"],
            "git_commit": pr["git_commit"],
            "pull_number": pr["pull_number"],
            "test_names": pr["test_names"],
        }
        results.append(pulls)
    return results


def filter_out_pr_results(results, pr_commit):
    """
    Filter out results that are not for the given PR commit.
    """
    # TODO: I don't think this is needed anymore?
    # Was needed. Now fixed the query but keep this for  a while
    # print(results)
    initial = len(results)
    filtered = list(
        filter(
            lambda x: "pull_request" not in x
            or x["attributes"]["git_commit"] == pr_commit,
            results,
        )
    )
    if len(filtered) < initial:
        logging.warning(
            "Filtered test results in python. This should happen at DB level."
        )
    return filtered
