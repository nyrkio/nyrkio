import asyncio
import pytest
from datetime import datetime

from backend.db.db import (
    DBStore,
    DBStoreAlreadyInitialized,
    DBStoreMissingRequiredKeys,
    DBStoreResultExists,
    MockDBStrategy,
)

from backend.auth.auth import add_user


def test_singleton_dbstore():
    """Ensure we only ever have one copy of DBStore."""
    store1 = DBStore()
    store2 = DBStore()
    assert store1 is store2


def test_dbstore_already_initialized():
    """Exceptions should be raised if we re-init a DBStore"""
    store = DBStore()
    store.setup(MockDBStrategy())

    with pytest.raises(DBStoreAlreadyInitialized):
        store.setup(MockDBStrategy())

    asyncio.run(store.startup())
    with pytest.raises(DBStoreAlreadyInitialized):
        asyncio.run(store.startup())


def test_invalid_primary_key():
    """Ensure that we can't use an invalid primary key when adding a result"""
    store = DBStore()
    strategy = MockDBStrategy()
    store.setup(strategy)
    asyncio.run(store.startup())

    user = strategy.get_test_user()
    with pytest.raises(DBStoreMissingRequiredKeys):
        asyncio.run(store.add_results(user.id, "benchmark1", [{"foo": "bar"}]))


def test_add_single_result():
    """Add a single test result"""
    store = DBStore()
    strategy = MockDBStrategy()
    store.setup(strategy)
    asyncio.run(store.startup())

    user = strategy.get_test_user()
    results = [
        {
            "timestamp": 1234,
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        }
    ]
    asyncio.run(store.add_results(user.id, "benchmark1", results))
    response, meta = asyncio.run(store.get_results(user.id, "benchmark1"))
    assert results == response


def test_create_doc_with_metadata():
    """Ensure that we create a doc with the correct metadata"""
    store = DBStore()
    strategy = MockDBStrategy()
    store.setup(strategy)
    asyncio.run(store.startup())

    user = strategy.get_test_user()
    test_name = "benchmark1"
    test_result = {
        "timestamp": 1234,
        "attributes": {
            "git_repo": "https://github.com/nyrkio/nyrkio",
            "branch": "main",
            "git_commit": "123456",
        },
    }
    doc = store.create_doc_with_metadata(test_result, user.id, test_name)

    assert doc["user_id"] == user.id
    assert doc["version"] == DBStore._VERSION
    assert doc["test_name"] == test_name

    d = doc["_id"]
    assert d["user_id"] == user.id
    assert d["git_repo"] == test_result["attributes"]["git_repo"]
    assert d["git_commit"] == test_result["attributes"]["git_commit"]
    assert d["branch"] == test_result["attributes"]["branch"]

    # The order of keys is critical. Make sure we don't change it
    assert list(d.keys()) == [
        "git_repo",
        "branch",
        "git_commit",
        "test_name",
        "timestamp",
        "user_id",
    ]

    # Ensure that we don't modify the original dict
    assert "user_id" not in test_result
    assert "version" not in test_result
    assert "test_name" not in test_result


def test_default_data_for_new_user():
    """Ensure that we add default data for a new user"""
    store = DBStore()
    strategy = MockDBStrategy()
    store.setup(strategy)
    asyncio.run(store.startup())

    user = strategy.get_test_user()

    # Ensure that the user has some test results
    test_names = asyncio.run(store.get_test_names(user.id))
    assert len(test_names) > 0
    assert "default_benchmark" in test_names

    # Lookup the data for benchmark1
    results, meta = asyncio.run(store.get_results(user.id, "default_benchmark"))
    assert results == [MockDBStrategy.DEFAULT_DATA]


def test_get_default_data():
    """Ensure that we can get the default data"""
    store = DBStore()
    strategy = MockDBStrategy()
    store.setup(strategy)
    asyncio.run(store.startup())

    results = asyncio.run(store.get_default_test_names())
    assert len(results) > 0
    assert "default_benchmark" in results

    # Ensure that the user has some test results
    results, meta = asyncio.run(store.get_default_data("default_benchmark"))
    assert len(results) > 0
    assert results == [MockDBStrategy.DEFAULT_DATA]


def test_get_default_data_with_invalid_test_name():
    """Ensure that we can't get any data if we supply an invalid testname"""
    store = DBStore()
    strategy = MockDBStrategy()
    store.setup(strategy)
    asyncio.run(store.startup())

    # Ensure that an invalid test name returns no results
    results, meta = asyncio.run(store.get_default_data("invalid_test_name"))
    assert len(results) == 0
    assert len(meta) == 0


def test_can_disable_change_detection_for_metrics():
    """Ensure that we can disable change detection for metrics"""
    store = DBStore()
    strategy = MockDBStrategy()
    store.setup(strategy)
    asyncio.run(store.startup())

    user = strategy.get_test_user()
    test_name = "benchmark1"
    metrics = ["foo", "bar"]
    asyncio.run(store.disable_changes(user.id, test_name, metrics))

    disabled = asyncio.run(store.get_disabled_metrics(user.id, test_name))
    assert set(disabled) == set(metrics)


def test_can_enable_prev_disabled_metric():
    """Ensure that we can enable a previously disabled metric"""
    store = DBStore()
    strategy = MockDBStrategy()
    store.setup(strategy)
    asyncio.run(store.startup())

    user = strategy.get_test_user()
    test_name = "benchmark1"
    disabled_metrics = ["foo", "bar"]
    asyncio.run(store.disable_changes(user.id, test_name, disabled_metrics))

    disabled = asyncio.run(store.get_disabled_metrics(user.id, test_name))
    assert set(disabled) == set(disabled_metrics)

    enabled_metrics = ["foo"]
    asyncio.run(store.enable_changes(user.id, test_name, enabled_metrics))

    disabled = asyncio.run(store.get_disabled_metrics(user.id, test_name))
    assert set(disabled) == set(disabled_metrics) - set(enabled_metrics)


def test_cannot_add_same_result_twice():
    """Ensure that we can't add the same result twice"""
    store = DBStore()
    strategy = MockDBStrategy()
    store.setup(strategy)
    asyncio.run(store.startup())

    user = strategy.get_test_user()
    test_name = "benchmark1"
    results = [
        {
            "timestamp": 1234,
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        }
    ]
    asyncio.run(store.add_results(user.id, test_name, results))

    with pytest.raises(DBStoreResultExists):
        asyncio.run(store.add_results(user.id, test_name, results))


def test_user_config():
    """Ensure that we can store and retrieve user configuration"""
    store = DBStore()
    strategy = MockDBStrategy()
    store.setup(strategy)
    asyncio.run(store.startup())

    user = strategy.get_test_user()
    config = {"foo": "bar"}
    asyncio.run(store.set_user_config(user.id, config))

    response, meta = asyncio.run(store.get_user_config(user.id))
    assert response == config


def test_get_user_config_with_no_config():
    """Ensure that we can get a default config if the user has no config"""
    store = DBStore()
    strategy = MockDBStrategy()
    store.setup(strategy)
    asyncio.run(store.startup())

    user = strategy.get_test_user()
    response, meta = asyncio.run(store.get_user_config(user.id))
    assert response == {}


def test_get_user_config_update_existing():
    """Ensure that we can update an existing user config"""
    store = DBStore()
    strategy = MockDBStrategy()
    store.setup(strategy)
    asyncio.run(store.startup())

    user = strategy.get_test_user()
    config = {"foo": "bar"}
    asyncio.run(store.set_user_config(user.id, config))

    response, meta = asyncio.run(store.get_user_config(user.id))
    assert response == config

    config = {"foo": "baz"}
    asyncio.run(store.set_user_config(user.id, config))

    response, meta = asyncio.run(store.get_user_config(user.id))
    assert response == config


def test_delete_user_config():
    """Ensure that we can delete a user config"""
    store = DBStore()
    strategy = MockDBStrategy()
    store.setup(strategy)
    asyncio.run(store.startup())

    user = strategy.get_test_user()
    config = {"foo": "bar"}
    asyncio.run(store.set_user_config(user.id, config))

    response, meta = asyncio.run(store.get_user_config(user.id))
    assert response == config

    asyncio.run(store.delete_user_config(user.id))

    response, meta = asyncio.run(store.get_user_config(user.id))
    assert response == {}


def test_get_all_test_names_without_user():
    """Ensure that we can get all test names without a user"""
    store = DBStore()
    strategy = MockDBStrategy()
    store.setup(strategy)
    asyncio.run(store.startup())

    user = strategy.get_test_user()
    test_name = "benchmark1"
    results = [
        {
            "timestamp": 1234,
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        }
    ]

    asyncio.run(store.add_results(user.id, test_name, results))

    user2 = asyncio.run(add_user("user2@foo.com", "password2"))
    test_name2 = "benchmark2"
    asyncio.run(store.add_results(user2.id, test_name2, results))

    response = asyncio.run(store.get_test_names())
    user_results = response[user.email]
    for t in (test_name, "default_benchmark"):
        assert t in user_results
    user2_results = response[user2.email]
    for t in (test_name2, "default_benchmark"):
        assert t in user2_results


def test_test_config():
    """Ensure that we can store and retrieve test configuration"""
    store = DBStore()
    strategy = MockDBStrategy()
    store.setup(strategy)
    asyncio.run(store.startup())

    user = strategy.get_test_user()
    test_name = "benchmark1"
    config = [
        {
            "public": True,
            "attributes": {
                "git_repo": "https://github.com/foo/bar",
                "branch": "main",
            },
        }
    ]
    asyncio.run(store.set_test_config(user.id, test_name, config))

    response, meta = asyncio.run(store.get_test_config(user.id, test_name))
    assert response == config

    # Test that we can update the config
    config = [
        {
            "public": False,
            "attributes": {
                "git_repo": "https://github.com/foo/bar",
                "branch": "main",
            },
        },
        {
            "public": True,
            "attributes": {
                "git_repo": "https://github.com/foo/bar",
                "branch": "dev",
            },
        },
    ]
    asyncio.run(store.set_test_config(user.id, test_name, config))

    response, meta = asyncio.run(store.get_test_config(user.id, test_name))
    assert response == config


def test_get_public_results():
    """Ensure that we can get public results"""
    store = DBStore()
    strategy = MockDBStrategy()
    store.setup(strategy)
    asyncio.run(store.startup())

    response, meta = asyncio.run(store.get_public_results())
    assert response == []

    test_name = "benchmark1"
    results = [
        {
            "timestamp": 1234,
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        }
    ]
    user = strategy.get_test_user()
    asyncio.run(store.add_results(user.id, test_name, results))

    config = [
        {
            "public": True,
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
            },
        }
    ]
    asyncio.run(store.set_test_config(user.id, test_name, config))

    response, meta = asyncio.run(store.get_public_results())
    expected = [
        {
            "user_id": user.id,
            "public": True,
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
            },
            "test_name": "benchmark1",
        }
    ]

    # Add another test for the same repository
    test_name = "benchmark2"
    results = [
        {
            "timestamp": 1234,
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        }
    ]
    asyncio.run(store.add_results(user.id, test_name, results))

    # Make benchmark2 public
    config = [
        {
            "public": True,
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
            },
        }
    ]

    asyncio.run(store.set_test_config(user.id, test_name, config))

    response, meta = asyncio.run(store.get_public_results())
    expected = [
        {
            "public": True,
            "user_id": user.id,
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
            },
            "test_name": "benchmark1",
        },
        {
            "public": True,
            "user_id": user.id,
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
            },
            "test_name": "benchmark2",
        },
    ]
    assert response[0] == expected[0]
    assert isinstance(meta[0]["last_modified"], datetime)
    assert response[1] == expected[1]
    assert isinstance(meta[1]["last_modified"], datetime)


def test_delete_test_config():
    """Ensure that we can delete a test config"""
    store = DBStore()
    strategy = MockDBStrategy()
    store.setup(strategy)
    asyncio.run(store.startup())

    user = strategy.get_test_user()
    test_name1 = "benchmark1"
    config = [
        {
            "public": True,
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
            },
        }
    ]
    asyncio.run(store.set_test_config(user.id, test_name1, config))

    test_name2 = "benchmark2"
    asyncio.run(store.set_test_config(user.id, test_name2, config))

    response, meta = asyncio.run(store.get_test_config(user.id, test_name1))
    assert response == config

    asyncio.run(store.delete_test_config(user.id, test_name1))
    asyncio.run(store.delete_test_config(user.id, test_name1))

    response, meta = asyncio.run(store.get_test_config(user.id, test_name1))
    assert response == []
    assert meta == []

    response, meta = asyncio.run(store.get_test_config(user.id, test_name2))
    assert response == config
    assert len(meta) == 1
    assert "last_modified" in meta[0] and isinstance(meta[0]["last_modified"], datetime)


def test_result_names_for_invalid_user():
    """Ensure that we can't get test names with an invalid user"""
    store = DBStore()
    strategy = MockDBStrategy()
    store.setup(strategy)
    asyncio.run(store.startup())

    test_name = "benchmark1"
    results = [
        {
            "timestamp": 1234,
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        }
    ]

    invalid_user_id = 7777
    asyncio.run(store.add_results(invalid_user_id, test_name, results))
    response = asyncio.run(store.get_test_names(None))
    assert response


def test_delete_result():
    """Ensure that we can delete a result"""
    store = DBStore()
    strategy = MockDBStrategy()
    store.setup(strategy)
    asyncio.run(store.startup())

    user = strategy.get_test_user()
    test_name = "benchmark1"
    results = [
        {
            "timestamp": 1234,
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        }
    ]

    asyncio.run(store.add_results(user.id, test_name, results))

    response, meta = asyncio.run(store.get_results(user.id, test_name))
    assert response == results
    assert all(list(isinstance(m["last_modified"], datetime) for m in meta))

    asyncio.run(store.delete_result(user.id, test_name, None))

    response, meta = asyncio.run(store.get_results(user.id, test_name))
    assert response == []
    assert meta == []


def test_delete_result_by_org():
    """Ensure that we can delete a result by org"""
    store = DBStore()
    strategy = MockDBStrategy()
    store.setup(strategy)
    asyncio.run(store.startup())

    user, _ = strategy.get_github_users()
    test_name = "benchmark1"
    results = [
        {
            "timestamp": 1234,
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        }
    ]

    def get_org_id(user, name):
        for account in user.oauth_accounts:
            for org in account.organizations:
                if org["login"] == name:
                    return org["id"]
        return None

    org_id = get_org_id(user, "nyrkio2")
    assert org_id

    asyncio.run(store.add_results(org_id, test_name, results))

    response, meta = asyncio.run(store.get_results(org_id, test_name))
    assert response == results
    assert all(list(isinstance(m["last_modified"], datetime) for m in meta))

    asyncio.run(store.delete_result(org_id, test_name, None))
