import asyncio
from backend.auth import auth


def test_test_user_can_login(client):
    client.login()


def test_invalid_user_cannot_login(unauthenticated_client):
    response = unauthenticated_client.post(
        "/api/v0/auth/jwt/login", data={"username": "bad@foo.com", "password": "foo"}
    )
    # should this be HTTP 401?
    assert response.status_code == 400


def test_create_new_user(unauthenticated_client):
    email = "newuser@foo.com"
    password = "somepass"
    headers = {"Content-type": "application/json"}
    response = unauthenticated_client.post(
        "/api/v0/auth/register",
        headers=headers,
        json={"email": email, "password": password},
    )
    assert response.status_code == 201


def test_get_user_by_email():
    email = "blah@foo.com"
    user = asyncio.run(auth.add_user(email, "foo"))
    u = asyncio.run(auth.get_user_by_email(email))
    assert user == u
