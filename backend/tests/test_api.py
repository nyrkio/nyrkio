def test_results(client):
    """Minimal test that includes logging in and getting a token"""
    response = client.get("/api/v0/results")
    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}

    client.login()
    response = client.get("/api/v0/results")
    assert response.status_code == 200
    assert response.json() == []


def test_results_methods(client):
    """Ensure that only the GET HTTP method works with /results"""
    client.login()
    response = client.get("/api/v0/results")
    assert response.status_code == 200
    assert response.json() == []

    response = client.put("/api/v0/results")
    assert response.status_code == 405
    assert response.json() == {"detail": "Method Not Allowed"}

    response = client.patch("/api/v0/results")
    assert response.status_code == 405
    assert response.json() == {"detail": "Method Not Allowed"}

    response = client.delete("/api/v0/results")
    assert response.status_code == 200
    assert response.json() == []


def test_get_non_existing_result(client):
    """Ensure that we get a 404 when trying to get a non-existing result"""
    client.login()
    response = client.get("/api/v0/result/benchmark1")
    assert response.json() == {"detail": "Not Found"}
    assert response.status_code == 404


def test_add_result(client):
    client.login()

    # Add a result
    data = [
        {
            "timestamp": 1,
            "metrics": {"metric1": 1.0, "metric2": 2.0},
            "attributes": {"attr1": "value1", "attr2": "value2"},
        }
    ]
    response = client.post("/api/v0/result/benchmark1", json=data)
    assert response.status_code == 200

    # Read back the result
    response = client.get("/api/v0/results")
    assert response.status_code == 200
    assert "benchmark1" == response.json()[0]["test_name"]

    response = client.get("/api/v0/result/benchmark1")
    assert response.status_code == 200
    json = response.json()
    assert len(json) == 1
    assert json[0] == data[0]


def test_add_multiple_test_results_at_once(client):
    """Upload multiple results in one POST request"""
    client.login()
    data = [
        {
            "timestamp": 1,
            "metrics": {"metric1": 1.0, "metric2": 2.0},
            "attributes": {"attr1": "value1", "attr2": "value2"},
        },
        {
            "timestamp": 2,
            "metrics": {"metric1": 2.0, "metric2": 3.0},
            "attributes": {"attr1": "value1", "attr2": "value2"},
        },
    ]
    response = client.post("/api/v0/result/benchmark1", json=data)
    assert response.status_code == 200

    response = client.get("/api/v0/results")
    assert response.status_code == 200
    assert "benchmark1" == response.json()[0]["test_name"]

    response = client.get("/api/v0/result/benchmark1")
    assert response.status_code == 200
    json = response.json()
    assert len(json) == 2
    assert data[0] in json
    assert data[1] in json


def test_delete_results(client):
    """Test that we can delete all a user's results"""
    client.login()

    # Add a result
    data = [
        {
            "timestamp": 1,
            "metrics": {"metric1": 1.0, "metric2": 2.0},
            "attributes": {"attr1": "value1", "attr2": "value2"},
        },
        {
            "timestamp": 2,
            "metrics": {"metric1": 2.0, "metric2": 3.0},
            "attributes": {"attr1": "value1", "attr2": "value2"},
        },
    ]
    response = client.post("/api/v0/result/benchmark1", json=data)
    assert response.status_code == 200

    # Read back the result
    response = client.get("/api/v0/results")
    assert response.status_code == 200
    assert "benchmark1" in response.json()[0]["test_name"]

    # Delete all results
    response = client.delete("/api/v0/results")
    assert response.status_code == 200

    # Read back the result
    response = client.get("/api/v0/results")
    assert response.status_code == 200
    assert response.json() == []
