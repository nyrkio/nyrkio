import os
import pytest

from starlette.testclient import TestClient
from httpx import Response
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
        self.email = "john@foo.com"

    def login(self):
        response = self.post(
            "/api/v0/auth/jwt/login", data={"username": self.email, "password": "foo"}
        )
        assert response.status_code == 200
        token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {token}"}

        # Delete default data. Tests that need this test data should
        # use the unauthenticated_client fixture.
        response = self.delete("/api/v0/result/default_benchmark")
        status = response.status_code
        assert status == 200 or status == 404

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
        assert self.headers, "You must call login() first"

        if "headers" in kwargs:
            kwargs["headers"] = {**self.headers, **kwargs["headers"]}
        else:
            kwargs["headers"] = self.headers

        return super().post(*args, **dict(kwargs))


class SuperuserClient(AuthenticatedTestClient):
    def __init__(self, app):
        super().__init__(app)
        self.email = "admin@foo.com"

    def login(self):
        response = self.post(
            "/api/v0/auth/jwt/login",
            data={"username": self.email, "password": "admin"},
        )
        assert response.status_code == 200
        token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {token}"}
        return response


class GitHubClient(AuthenticatedTestClient):
    def __init__(self, app):
        super().__init__(app)
        self.email = "gh@foo.com"

    def login(self):
        response = self.post(
            "/api/v0/auth/jwt/login",
            data={"username": self.email, "password": "gh"},
        )
        assert response.status_code == 200
        token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {token}"}
        return response


class MockHttpClient(TestClient):
    """
    Capture and mock all http requests anywhere in the world.
    """

    def __init__(self, app):
        super().__init__(app)
        self.mock_response_dict = {
            "status_code": 200,
            "text": '{"payload": "mock payload"}',
            "content": b'{"payload": "mock payload"}',
        }

    def mock_response(self, **kwargs):
        self.mock_response_dict = kwargs

    def method(self, method, url, **kwargs):
        valid_args = [
            "content",
            "data",
            "files",
            "json",
            "headers",
            "cookies",
            "auth",
            "proxy",
            "timeout",
            "follow_redirects",
            "verify",
            "trust_env",
        ]

        for k, v in kwargs.items():
            print(k, v)
            assert k in valid_args

        print("Create Response object")
        print(self.mock_response_dict)
        print(kwargs)
        resp = Response(**self.mock_response_dict)  # , **kwargs)
        return resp

    def get(self, url, **kwargs):
        return self.method("GET", url, **kwargs)

    def post(self, url, **kwargs):
        print(kwargs)
        print(*kwargs)
        # print(**kwargs)
        return self.method("POST", url, **kwargs)

    def put(self, url, **kwargs):
        return self.method("PUT", url, **kwargs)

    def delete(self, url, **kwargs):
        return self.method("DELETE", url, **kwargs)


@pytest.fixture
def client():
    with AuthenticatedTestClient(app) as client:
        yield client
        # Delete all results after each test
        client.delete("/api/v0/results")


@pytest.fixture
def superuser_client():
    with SuperuserClient(app) as client:
        yield client
        # Delete all results after each test
        client.delete("/api/v0/results")


@pytest.fixture
def unauthenticated_client():
    with TestClient(app) as client:
        yield client


@pytest.fixture
def gh_client():
    with GitHubClient(app) as client:
        yield client


@pytest.fixture
def mock_http_client():
    with MockHttpClient(app) as client:
        yield client
