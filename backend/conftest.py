import pytest


@pytest.fixture
def client():
    from starlette.testclient import TestClient
    from .api import app

    client = TestClient(app)
    return client
