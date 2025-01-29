import asyncio
import copy
import pytest
from datetime import datetime

from backend.db.db import (
    DBStore,
    DBStoreAlreadyInitialized,
    DBStoreMissingRequiredKeys,
    DBStoreResultExists,
    MockDBStrategy,
    separate_meta,
    separate_meta_one,
    build_pulls,
    filter_out_pr_results,
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
            "metrics": [{"name": "metric1", "value": 5, "unit": "ms"}],
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


def test_add_single_with_trailing_slash():
    """Add a single test result"""
    store = DBStore()
    strategy = MockDBStrategy()
    store.setup(strategy)
    asyncio.run(store.startup())

    user = strategy.get_test_user()
    results = [
        {
            "timestamp": 1234,
            "metrics": [{"name": "metric1", "value": 5, "unit": "ms"}],
            "attributes": {
                "git_repo": "https://GitHub.com/nyrkio/nyrkio/",
                "branch": "main",
                "git_commit": "123456",
            },
        }
    ]
    asyncio.run(store.add_results(user.id, "benchmark1", results))
    response, meta = asyncio.run(store.get_results(user.id, "benchmark1"))
    assert response[0]["attributes"]["git_repo"] == "https://github.com/nyrkio/nyrkio"
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
        "metrics": [{"name": "metric1", "value": 5, "unit": "ms"}],
        "attributes": {
            "git_repo": "https://github.com/nyrkio/nyrkio",
            "branch": "main",
            "git_commit": "123456",
        },
    }
    doc = store.create_doc_with_metadata(test_result, user.id, test_name, None)

    def assert_document_metadata(document):
        assert document["user_id"] == user.id
        assert document["version"] == DBStore._VERSION
        assert document["test_name"] == test_name

        d = document["_id"]
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

    assert_document_metadata(doc)

    # Ensure that we don't modify the original dict
    assert "user_id" not in test_result
    assert "version" not in test_result
    assert "test_name" not in test_result

    doc = store.create_doc_with_metadata(test_result, user.id, test_name, 123)
    assert doc["pull_request"] == 123
    assert_document_metadata(doc)


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
    assert results == MockDBStrategy.DEFAULT_DATA


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
    assert results == MockDBStrategy.DEFAULT_DATA


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
            "metrics": [{"name": "metric1", "value": 5, "unit": "ms"}],
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
            "metrics": [{"name": "metric1", "value": 5, "unit": "ms"}],
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
            "metrics": [{"name": "metric1", "value": 5, "unit": "ms"}],
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
            "metrics": [{"name": "metric1", "value": 5, "unit": "ms"}],
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
            "metrics": [{"name": "metric1", "value": 5, "unit": "ms"}],
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
            "metrics": [{"name": "metric1", "value": 5, "unit": "ms"}],
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
            "metrics": [{"name": "metric1", "value": 5, "unit": "ms"}],
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


def test_data_without_meta_field():
    """Ensure that we can get data without a meta field"""
    store = DBStore()
    strategy = MockDBStrategy()
    store.setup(strategy)
    asyncio.run(store.startup())

    user = strategy.get_test_user()
    test_name = "benchmark1"
    results = [
        {
            "timestamp": 1234,
            "metrics": [{"name": "metric1", "value": 5, "unit": "ms"}],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        }
    ]
    new_list = [
        DBStore.create_doc_with_metadata(r, user.id, test_name) for r in results
    ]
    test_results = store.db.test_results

    # Simulate an old version of the data
    for r in new_list:
        del r["meta"]

    asyncio.run(test_results.insert_many(new_list))

    db_results = asyncio.run(store.get_results(user.id, test_name))
    assert db_results[0][0]["timestamp"] == results[0]["timestamp"]


def test_separate_meta():
    """Ensure that we can separate data and metadata"""
    aggregated_data = [
        {"foo": "bar", "timestamp": 1234, "meta": {"baz": "qux"}},
        {"foo": "bar", "timestamp": 5678, "meta": {"baz": "qux"}},
    ]

    def check_data(d, m):
        assert len(d) == len(m)
        for dat in d:
            assert "meta" not in dat

    data, metadata = separate_meta_one(aggregated_data[0])
    check_data([data], [metadata])

    data, metadata = separate_meta(aggregated_data)
    check_data(data, metadata)
    assert metadata[0]["baz"] == "qux"
    assert metadata[1]["baz"] == "qux"

    data, metadata = separate_meta([])
    check_data(data, metadata)

    data, metadata = separate_meta([{"foo": "bar"}])
    check_data(data, metadata)


def test_update_existing_result():
    """Ensure that we can update an existing result"""
    store = DBStore()
    strategy = MockDBStrategy()
    store.setup(strategy)
    asyncio.run(store.startup())

    user = strategy.get_test_user()
    test_name = "benchmark1"
    results = [
        {
            "timestamp": 1234,
            "metrics": [{"name": "metric1", "value": 5, "unit": "ms"}],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        }
    ]

    asyncio.run(store.add_results(user.id, test_name, results))
    response, _ = asyncio.run(store.get_results(user.id, test_name))
    assert response == results

    results[0]["metrics"][0]["value"] = 2

    asyncio.run(store.add_results(user.id, test_name, results, update=True))
    response, _ = asyncio.run(store.get_results(user.id, test_name))
    assert response == results


def test_pull_number():
    """Ensure that we can store and retrieve results with pull numbers"""
    store = DBStore()
    strategy = MockDBStrategy()
    store.setup(strategy)
    asyncio.run(store.startup())

    user = strategy.get_test_user()
    test_name = "benchmark1"
    pull_number = 123
    results = [
        {
            "timestamp": 1,
            "metrics": [{"name": "metric1", "value": 5, "unit": "ms"}],
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
        }
    ]

    # Add pr result
    asyncio.run(store.add_results(user.id, test_name, results, pull_number=pull_number))

    # Add regular main branch result
    results[0]["timestamp"] = 2
    asyncio.run(store.add_results(user.id, test_name, results))

    # Ensure we don't see the pull request result
    response, _ = asyncio.run(store.get_results(user.id, test_name))
    assert len(response) == 1
    assert response[0]["timestamp"] == 2

    # Ensure we can see the pull request result and the regular result
    response, _ = asyncio.run(store.get_results(user.id, test_name, pull_number))
    assert len(response) == 2
    assert response[0]["timestamp"] == 1
    assert response[1]["timestamp"] == 2

    results[0]["timestamp"] = 3
    asyncio.run(store.add_results(user.id, test_name, results, pull_number=456))

    # Ensure pr 456 isn't visible
    response, _ = asyncio.run(store.get_results(user.id, test_name, pull_number))
    assert len(response) == 2
    assert response[0]["timestamp"] == 1
    assert response[1]["timestamp"] == 2

    # Should we both the pull request (456) result and the regular main branch result
    response, _ = asyncio.run(store.get_results(user.id, test_name, 456))
    assert len(response) == 2
    assert response[0]["timestamp"] == 2
    assert response[1]["timestamp"] == 3


def test_pr_add_tests():
    """Ensure that we can add tests for a pr and commit"""
    store = DBStore()
    strategy = MockDBStrategy()
    store.setup(strategy)
    asyncio.run(store.startup())

    user = strategy.get_test_user()
    test_names = ["benchmark1", "benchmark2"]
    pull_number = 123
    git_commit = "123456"
    repo = "https://github.com/nyrkio/nyrkio"

    for t in test_names:
        asyncio.run(store.add_pr_test_name(user.id, repo, git_commit, pull_number, t))
    results = asyncio.run(
        store.get_pull_requests(user.id, repo, git_commit, pull_number)
    )

    assert results == [
        {
            "git_repo": repo,
            "git_commit": git_commit,
            "pull_number": pull_number,
            "test_names": test_names,
        }
    ]


def test_pr_get_pull_requests():
    """Ensure that we can get test names for a pr and commit"""
    store = DBStore()
    strategy = MockDBStrategy()
    store.setup(strategy)
    asyncio.run(store.startup())

    user = strategy.get_test_user()
    test_name = "benchmark1"
    pull_number = 123
    git_commit = "123456"
    repo = "https://github.com/nyrkio/nyrkio"

    asyncio.run(
        store.add_pr_test_name(user.id, repo, git_commit, pull_number, test_name)
    )

    results = asyncio.run(store.get_pull_requests(user.id))
    assert results == [
        {
            "git_repo": repo,
            "git_commit": git_commit,
            "pull_number": pull_number,
            "test_names": [test_name],
        }
    ]


def test_pulls_func():
    """
    Test the function to build a "pulls" object from the pr_tests collection.
    """
    repo1 = "https://github.com/nyrkio/nyrkio"
    repo2 = "https://github.com/nyrkio/nyrkio2"
    git_commit = "123456"
    test_names1 = ["benchmark1", "benchmark2"]
    test_names2 = ["benchmark3", "benchmark4"]
    results = [
        {
            "_id": None,
            "user_id": 1,
            "git_repo": repo1,
            "test_names": test_names1,
            "git_commit": git_commit,
            "pull_number": 1,
        },
        {
            "_id": None,
            "user_id": 1,
            "git_repo": repo2,
            "test_names": test_names2,
            "git_commit": git_commit,
            "pull_number": 1,
        },
    ]

    pulls = build_pulls(results)
    assert pulls == [
        {
            "git_repo": repo1,
            "test_names": test_names1,
            "git_commit": git_commit,
            "pull_number": 1,
        },
        {
            "git_repo": repo2,
            "test_names": test_names2,
            "git_commit": git_commit,
            "pull_number": 1,
        },
    ]


def test_get_results_with_exact_pr_commit():
    """Ensure that we can get results for a specific pr and commit"""
    store = DBStore()
    strategy = MockDBStrategy()
    store.setup(strategy)
    asyncio.run(store.startup())

    user = strategy.get_test_user()
    test_name = "benchmark1"
    pull_number = 123
    git_commit = "123456"
    repo = "https://github.com/nyrkio/nyrkio"

    results = [
        {
            "timestamp": 1,
            "metrics": [{"name": "metric1", "value": 5, "unit": "ms"}],
            "attributes": {
                "git_repo": repo,
                "branch": "main",
                "git_commit": git_commit,
            },
        }
    ]

    asyncio.run(store.add_results(user.id, test_name, results))
    results[0]["timestamp"] = 2
    asyncio.run(store.add_results(user.id, test_name, results, pull_number=pull_number))

    data, _ = asyncio.run(
        store.get_results(user.id, test_name, pull_number, git_commit)
    )
    assert len(data) == 2
    results[0]["timestamp"] = 3
    results[0]["attributes"]["git_commit"] = "abcdef"
    asyncio.run(store.add_results(user.id, test_name, results, pull_number=pull_number))

    data, _ = asyncio.run(
        store.get_results(user.id, test_name, pull_number, git_commit)
    )
    assert len(data) == 2


def test_filter_out_pr_results():
    """Ensure that we can filter out pr results"""
    results = [
        {"metrics": {"foo": 1}, "attributes": {"git_commit": "foo"}},
        {"metrics": {"foo": 2}, "attributes": {"git_commit": "bar"}},
        {
            "metrics": {"foo": 3},
            "attributes": {"git_commit": "baz"},
            "pull_request": 123,
        },
        {
            "metrics": {"foo": 4},
            "attributes": {"git_commit": "bam"},
            "pull_request": 123,
        },
    ]

    filtered = filter_out_pr_results(results, "baz")
    assert len(filtered) == 3

    filtered = filter_out_pr_results(results, "bam")
    assert len(filtered) == 3


def test_missing_keys():
    """Ensure that we raise an exception if we're missing required keys"""
    store = DBStore()
    strategy = MockDBStrategy()
    store.setup(strategy)
    asyncio.run(store.startup())

    user = strategy.get_test_user()
    test_name = "benchmark1"
    legit_result = [
        {
            "timestamp": 1234,
            "attributes": {
                "git_repo": "https://github.com/nyrkio/nyrkio",
                "branch": "main",
                "git_commit": "123456",
            },
            "metrics": [{"name": "metric1", "unit": "unit1", "value": 1}],
        }
    ]

    with pytest.raises(DBStoreMissingRequiredKeys):
        missing_timestamp = copy.deepcopy(legit_result)
        del missing_timestamp[0]["timestamp"]
        asyncio.run(store.add_results(user.id, test_name, missing_timestamp))

    with pytest.raises(DBStoreMissingRequiredKeys):
        missing_git_repo = copy.deepcopy(legit_result)
        del missing_git_repo[0]["attributes"]["git_repo"]
        asyncio.run(store.add_results(user.id, test_name, missing_git_repo))

    with pytest.raises(DBStoreMissingRequiredKeys):
        missing_branch = copy.deepcopy(legit_result)
        del missing_branch[0]["attributes"]["branch"]
        asyncio.run(store.add_results(user.id, test_name, missing_branch))

    with pytest.raises(DBStoreMissingRequiredKeys):
        missing_git_commit = copy.deepcopy(legit_result)
        del missing_git_commit[0]["attributes"]["git_commit"]
        asyncio.run(store.add_results(user.id, test_name, missing_git_commit))

    with pytest.raises(DBStoreMissingRequiredKeys):
        missing_metric_name = legit_result.copy()
        del missing_metric_name[0]["metrics"][0]["name"]
        asyncio.run(store.add_results(user.id, test_name, missing_metric_name))

    with pytest.raises(DBStoreMissingRequiredKeys):
        missing_metric_value = legit_result.copy()
        del missing_metric_value[0]["metrics"][0]["value"]
        asyncio.run(store.add_results(user.id, test_name, missing_metric_value))

    with pytest.raises(DBStoreMissingRequiredKeys):
        missing_metric_unit = legit_result.copy()
        del missing_metric_unit[0]["metrics"][0]["unit"]
        asyncio.run(store.add_results(user.id, test_name, missing_metric_unit))
