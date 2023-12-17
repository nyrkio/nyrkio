import asyncio
import pytest

from backend.db.db import (
    DBStore,
    DBStoreAlreadyInitialized,
    TestDBStrategy,
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
