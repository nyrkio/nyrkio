import asyncio
import pytest

from backend.db.db import (
    DBStore,
    DBStoreAlreadyInitialized,
    MockDBStrategy,
)


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


def test_add_single_result():
    """Add a single test result"""
    store = DBStore()
    strategy = MockDBStrategy()
    store.setup(strategy)
    asyncio.run(store.startup())

    user = strategy.get_test_user()
    results = [{"foo": "bar"}]
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
    test_result = {"foo": "bar"}
    doc = store.create_doc_with_metadata(test_result, user, test_name)

    assert doc["user_id"] == user.id
    assert doc["version"] == DBStore._VERSION
    assert doc["test_name"] == test_name

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
    assert results[0]["foo"] == "bar"


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
    assert {"foo": "bar"} in results
    assert results[0]["foo"] == "bar"


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
