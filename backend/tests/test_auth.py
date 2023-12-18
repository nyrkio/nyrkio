def test_test_user_can_login(client):
    client.login()


def test_invalid_user_cannot_login(unauthenticated_client):
    response = unauthenticated_client.post(
        "/api/v0/auth/jwt/login", data={"username": "bad@foo.com", "password": "foo"}
    )
    # should this be HTTP 401?
    assert response.status_code == 400
