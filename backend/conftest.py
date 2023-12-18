import os
import pytest

from starlette.testclient import TestClient
from backend.api.api import app

os.environ["NYRKIO_TESTING"] = "True"


# https://docs.pytest.org/en/latest/example/simple.html#detect-if-running-from-within-a-pytest-run
def pytest_configure(config):
    from backend.db import db

    db._TESTING = True


class AuthenticatedTestClient(TestClient):
    """
    A simple wrapper around starlette.testclient that provides login helpers.
    """

    def __init__(self, app):
        super().__init__(app)
        self.headers = None

    def login(self):
        response = self.post(
            "/api/v0/auth/jwt/login",
            data={"username": "john@foo.com", "password": "foo"},
        )
        assert response.status_code == 200
        token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {token}"}
        return response

    def get_headers(self):
        return self.headers

    def get(self, *args, **kwargs):
        assert (
            "headers" not in kwargs.keys()
        ), "Cannot pass headers explicitly to AuthenicatedTestClient.get()"
        assert self.headers, "You must call login() first"
        return super().get(*args, **dict(kwargs, headers=self.headers))

    def post(self, *args, **kwargs):
        assert (
            "headers" not in kwargs.keys()
        ), "Cannot pass headers explicitly to AuthenicatedTestClient.get()"
        assert self.headers, "You must call login() first"
        return super().post(*args, **dict(kwargs, headers=self.headers))


@pytest.fixture
def client():
    with AuthenticatedTestClient(app) as client:
        yield client
        # Delete all results after each test
        client.delete("/api/v0/results")


@pytest.fixture
def unauthenticated_client():
    with TestClient(app) as client:
        yield client
