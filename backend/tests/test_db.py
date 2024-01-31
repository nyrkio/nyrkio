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
