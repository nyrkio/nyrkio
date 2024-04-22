def test_add_and_get_user_config(client):
    """Ensure that we can store and retrieve user configuration"""
    client.login()
    config = {
        "notifiers": {
            "slack": True,
        }
    }
    response = client.post("/api/v0/user/config", json=config)
    assert response.status_code == 200

    response = client.get("/api/v0/user/config")
    assert response.status_code == 200
    assert response.json() == {**config, "core": None}


def test_update_existing_user_config(client):
    """Ensure that we can update an existing user configuration"""
    client.login()
    config = {
        "notifiers": {
            "slack": True,
        }
    }
    response = client.post("/api/v0/user/config", json=config)
    assert response.status_code == 200

    response = client.get("/api/v0/user/config")
    assert response.status_code == 200
    assert response.json() == {**config, "core": None}

    new_config = {"notifiers": {"slack": False}}
    response = client.put("/api/v0/user/config", json=new_config)
    assert response.status_code == 200

    response = client.get("/api/v0/user/config")
    assert response.status_code == 200
    assert response.json() == {**new_config, "core": None}


def test_user_config_set_min_magnitude_max_pvalue(client):
    """Ensure that we can set min_magnitude and max_pvalue in user config"""
    client.login()
    config = {
        "core": {
            "min_magnitude": 0.5,
            "max_pvalue": 0.01,
        }
    }
    response = client.post("/api/v0/user/config", json=config)
    assert response.status_code == 200

    response = client.get("/api/v0/user/config")
    assert response.status_code == 200

    assert response.json() == {**config, "notifiers": None}


def test_user_config_set_max_pvalue_invalid(client):
    """Ensure that we can't set invalid max_pvalue in user config"""
    client.login()
    config = {
        "core": {
            "min_magnitude": 0.5,
            "max_pvalue": 1.01,
        }
    }
    response = client.post("/api/v0/user/config", json=config)
    assert response.status_code == 400
    assert response.json() == {"detail": "max_pvalue must be less than or equal to 1.0"}
