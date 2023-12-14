import pytest


@pytest.fixture
def client():
    from starlette.testclient import TestClient
    from .api.api import app

    client = TestClient(app)
    return client
