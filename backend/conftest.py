import pytest


def pytest_configure(config):
    from backend.db import db

    db.TESTING = True


@pytest.fixture
def client():
    from starlette.testclient import TestClient
    from .api.api import app

    client = TestClient(app)
    return client
