def test_results(client):
    """Minimal test that includes logging in and getting a token"""
    response = client.get("/api/v0/results")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

    response = client.post(
        "/token", data={"username": "johndoe", "password": "secret"}
    )
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v0/results", headers=headers)
    assert response.status_code == 200
    assert response.json() == {}

def test_results_methods(client):
    """Ensure that only the GET HTTP method works with /results"""
    response = client.get("/api/v0/results")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

    response = client.post(
        "/token", data={"username": "johndoe", "password": "secret"}
    )
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v0/results", headers=headers)
    assert response.status_code == 200
    assert response.json() == {}

    response = client.put("/api/v0/results", headers=headers)
    assert response.status_code == 405
    assert response.json() == {"detail": "Method Not Allowed"}

    response = client.patch("/api/v0/results", headers=headers)
    assert response.status_code == 405
    assert response.json() == {"detail": "Method Not Allowed"}

    response = client.delete("/api/v0/results", headers=headers)
    assert response.status_code == 405
    assert response.json() == {"detail": "Method Not Allowed"}
