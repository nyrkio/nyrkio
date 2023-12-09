import pytest


@pytest.fixture
def client():
    from starlette.testclient import TestClient
    from .main import app

    client = TestClient(app)
    return client
