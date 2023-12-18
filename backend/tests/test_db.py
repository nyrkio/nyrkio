import asyncio
import pytest

from backend.db.db import (
    DBStore,
    DBStoreAlreadyInitialized,
    TestDBStrategy,
    User,
)


def test_singleton_dbstore():
    """Ensure we only ever have one copy of DBStore."""
    store1 = DBStore()
    store2 = DBStore()
    assert store1 is store2


def test_dbstore_already_initialized():
    """Exceptions should be raised if we re-init a DBStore"""
    store = DBStore()
    store.setup(TestDBStrategy())

    with pytest.raises(DBStoreAlreadyInitialized):
        store.setup(TestDBStrategy())

    asyncio.run(store.startup())
    with pytest.raises(DBStoreAlreadyInitialized):
        asyncio.run(store.startup())


def test_add_single_result():
    """Add a single test result"""
    store = DBStore()
    strategy = TestDBStrategy()
    store.setup(strategy)
    asyncio.run(store.startup())

    user = strategy.get_test_user()
    results = [{"foo": "bar"}]
    asyncio.run(store.add_results(user, "benchmark1", results))
    response = asyncio.run(store.get_results(user, "benchmark1"))

    assert results == response