def test_unauthenticated_users_cannot_access_protected_routes(client):
    response = client.get("/users/me")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_authenticated_users_can_access_protected_routes(client):
    response = client.post(
        "/token", data={"username": "johndoe", "password": "secret"}
    )
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200
    expected_fields = {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
    }

    assert all(item in response.json().items()
               for item in expected_fields.items())
