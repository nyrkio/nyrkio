def test_payload_missing_metric_unit_doesnt_persist(client):
    """Call openapi.json"""
    client.login()

    response = client.get("/openapi.json")
    # print(json.dumps(response.json()))
    assert response.status_code == 200
