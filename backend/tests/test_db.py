import asyncio
import pytest

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
        asyncio.run(store.add_results(user, "benchmark1", [{"foo": "bar"}]))


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
    asyncio.run(store.add_results(user, "benchmark1", results))
    response = asyncio.run(store.get_results(user, "benchmark1"))
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
    doc = store.create_doc_with_metadata(test_result, user, test_name)

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
    test_names = asyncio.run(store.get_test_names(user))
    assert len(test_names) > 0
    assert "default_benchmark" in test_names

    # Lookup the data for benchmark1
    results = asyncio.run(store.get_results(user, "default_benchmark"))
    assert len(results) == 1
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
    results = asyncio.run(store.get_default_data("default_benchmark"))
    assert len(results) > 0
    assert results == [MockDBStrategy.DEFAULT_DATA]


def test_get_default_data_with_invalid_test_name():
    """Ensure that we can't get any data if we supply an invalid testname"""
    store = DBStore()
    strategy = MockDBStrategy()
    store.setup(strategy)
    asyncio.run(store.startup())

    # Ensure that an invalid test name returns no results
    results = asyncio.run(store.get_default_data("invalid_test_name"))
    assert len(results) == 0


def test_can_disable_change_detection_for_metrics():
    """Ensure that we can disable change detection for metrics"""
    store = DBStore()
    strategy = MockDBStrategy()
    store.setup(strategy)
    asyncio.run(store.startup())

    user = strategy.get_test_user()
    test_name = "benchmark1"
    metrics = ["foo", "bar"]
    asyncio.run(store.disable_changes(user, test_name, metrics))

    disabled = asyncio.run(store.get_disabled_metrics(user, test_name))
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
    asyncio.run(store.disable_changes(user, test_name, disabled_metrics))

    disabled = asyncio.run(store.get_disabled_metrics(user, test_name))
    assert set(disabled) == set(disabled_metrics)

    enabled_metrics = ["foo"]
    asyncio.run(store.enable_changes(user, test_name, enabled_metrics))

    disabled = asyncio.run(store.get_disabled_metrics(user, test_name))
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
    asyncio.run(store.add_results(user, test_name, results))

    with pytest.raises(DBStoreResultExists):
        asyncio.run(store.add_results(user, test_name, results))


def test_user_config():
    """Ensure that we can store and retrieve user configuration"""
    store = DBStore()
    strategy = MockDBStrategy()
    store.setup(strategy)
    asyncio.run(store.startup())

    user = strategy.get_test_user()
    config = {"foo": "bar"}
    asyncio.run(store.set_user_config(user, config))

    response = asyncio.run(store.get_user_config(user))
    assert response == config


def test_get_user_config_with_no_config():
    """Ensure that we can get a default config if the user has no config"""
    store = DBStore()
    strategy = MockDBStrategy()
    store.setup(strategy)
    asyncio.run(store.startup())

    user = strategy.get_test_user()
    response = asyncio.run(store.get_user_config(user))
    assert response == {}


def test_get_user_config_update_existing():
    """Ensure that we can update an existing user config"""
    store = DBStore()
    strategy = MockDBStrategy()
    store.setup(strategy)
    asyncio.run(store.startup())

    user = strategy.get_test_user()
    config = {"foo": "bar"}
    asyncio.run(store.set_user_config(user, config))

    response = asyncio.run(store.get_user_config(user))
    assert response == config

    config = {"foo": "baz"}
    asyncio.run(store.set_user_config(user, config))

    response = asyncio.run(store.get_user_config(user))
    assert response == config


def test_delete_user_config():
    """Ensure that we can delete a user config"""
    store = DBStore()
    strategy = MockDBStrategy()
    store.setup(strategy)
    asyncio.run(store.startup())

    user = strategy.get_test_user()
    config = {"foo": "bar"}
    asyncio.run(store.set_user_config(user, config))

    response = asyncio.run(store.get_user_config(user))
    assert response == config

    asyncio.run(store.delete_user_config(user))

    response = asyncio.run(store.get_user_config(user))
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

    asyncio.run(store.add_results(user, test_name, results))

    user2 = asyncio.run(add_user("user2@foo.com", "password2"))
    test_name2 = "benchmark2"
    asyncio.run(store.add_results(user2, test_name2, results))

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
    asyncio.run(store.set_test_config(user, test_name, config))

    response = asyncio.run(store.get_test_config(user, test_name))
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
    asyncio.run(store.set_test_config(user, test_name, config))

    response = asyncio.run(store.get_test_config(user, test_name))
    assert response == config


def test_get_public_results():
    """Ensure that we can get public results"""
    store = DBStore()
    strategy = MockDBStrategy()
    store.setup(strategy)
    asyncio.run(store.startup())

    response = asyncio.run(store.get_public_results())
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
    asyncio.run(store.add_results(user, test_name, results))

    config = [
        {
            "public": True,
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
            },
        }
    ]
    asyncio.run(store.set_test_config(user, test_name, config))

    response = asyncio.run(store.get_public_results())
    expected = [
        {
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
            },
            "test_name": "benchmark1",
        }
    ]
    assert response == expected

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
    asyncio.run(store.add_results(user, test_name, results))

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

    asyncio.run(store.set_test_config(user, test_name, config))

    response = asyncio.run(store.get_public_results())
    expected = [
        {
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
            },
            "test_name": "benchmark1",
        },
        {
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
            },
            "test_name": "benchmark2",
        },
    ]
    assert response == expected


def test_update_public_map():
    """Ensure that we can update the public map"""
    store = DBStore()
    strategy = MockDBStrategy()
    store.setup(strategy)
    asyncio.run(store.startup())

    public_test_name = "org/repo/branch/benchmark1"
    user = strategy.get_test_user()
    asyncio.run(store.set_public_map(public_test_name, user, True))

    response = asyncio.run(store.get_public_user(public_test_name))
    assert response == user.id

    asyncio.run(store.set_public_map(public_test_name, user, False))
    response = asyncio.run(store.get_public_user(public_test_name))
    assert response is None


def test_update_public_map_different_users():
    """Verify that a second user cannot create a map if one exists"""
    store = DBStore()
    strategy = MockDBStrategy()
    store.setup(strategy)
    asyncio.run(store.startup())

    public_test_name = "org/repo/branch/benchmark1"
    user = strategy.get_test_user()
    asyncio.run(store.set_public_map(public_test_name, user, True))
    # This should effectively be a nop
    asyncio.run(store.set_public_map(public_test_name, user, True))

    user2 = asyncio.run(add_user("user2@foo.com", "foo"))
    with pytest.raises(DBStoreResultExists):
        asyncio.run(store.set_public_map(public_test_name, user2, True))


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

    asyncio.run(store.set_test_config(user, test_name1, config))

    test_name2 = "benchmark2"
    asyncio.run(store.set_test_config(user, test_name2, config))

    response = asyncio.run(store.get_test_config(user, test_name1))
    assert response == config

    asyncio.run(store.delete_test_config(user, test_name1))
    asyncio.run(store.delete_test_config(user, test_name1))

    response = asyncio.run(store.get_test_config(user, test_name1))
    assert response == []

    response = asyncio.run(store.get_test_config(user, test_name2))
    assert response == config
