import json


def test_impersonate_other_user(superuser_client):
    superuser_client.login()

    response = superuser_client.get("/api/v0/admin/impersonate")
    response.raise_for_status()
    data = response.json()
    print(data)
    assert data["user_email"] == "admin@foo.com"
    assert "superuser" not in data

    user_id = "Need to find this out it changes every time"
    response = superuser_client.get("/api/v0/admin/all_users")
    response.raise_for_status()
    data = response.json()
    print(data)
    for u in data:
        if u["email"] == "john@foo.com":
            user_id = u["_id"]

    response = superuser_client.post(
        "/api/v0/admin/impersonate",
        data=json.dumps({"username": "john@foo.com", "id": user_id}),
    )

    data = response.json()
    print(data)
    response.raise_for_status()
    assert data["user_email"] == "john@foo.com"
    assert data["superuser"]["user_email"] == "admin@foo.com"

    response = superuser_client.get("/api/v0/admin/impersonate")
    response.raise_for_status()
    data = response.json()
    assert data["user_email"] == "john@foo.com"
    assert data["superuser"]["user_email"] == "admin@foo.com"

    response = superuser_client.delete("/api/v0/admin/impersonate")
    response.raise_for_status()
    data = response.json()
    assert data["user_email"] == "admin@foo.com"
    assert data["yourself"] is True
