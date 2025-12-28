import asyncio

from conftest import AuthenticatedTestClient, app

from backend.auth import auth


def test_add_and_get_user_config(client):
    """Ensure that we can store and retrieve user configuration"""
    client.login()
    config = {
        "notifiers": {
            "slack": True,
            "github_pr": False,
            "github": False,
            "since_days": 14,
        }
    }
    response = client.post("/api/v0/user/config", json=config)
    assert response.status_code == 200

    response = client.get("/api/v0/user/config")
    assert response.status_code == 200
    json = response.json()
    assert json == {
        **config,
        "billing": None,
    }

    config = {"core": {"max_pvalue": 0.00001, "min_magnitude": 0.5}}
    response = client.post("/api/v0/user/config", json=config)
    assert response.status_code == 200

    response = client.get("/api/v0/user/config")
    assert response.status_code == 200
    json = response.json()
    assert json == {
        **config,
        "notifiers": {
            "github_pr": False,
            "github": False,
            "since_days": 14,
            "slack": True,
        },
        "billing": None,
    }


def test_update_existing_user_config(client):
    """Ensure that we can update an existing user configuration"""
    client.login()
    config = {
        "notifiers": {
            "slack": True,
            "github_pr": False,
            "github": False,
            "since_days": 14,
        }
    }
    response = client.post("/api/v0/user/config", json=config)
    assert response.status_code == 200

    response = client.get("/api/v0/user/config")
    assert response.status_code == 200
    json = response.json()
    assert json == {
        **config,
        "billing": None,
    }

    new_config = {
        "notifiers": {
            "slack": False,
            "github_pr": False,
            "github": True,
            "since_days": 45,
        }
    }
    response = client.put("/api/v0/user/config", json=new_config)
    assert response.status_code == 200

    response = client.get("/api/v0/user/config")
    assert response.status_code == 200
    json = response.json()
    assert json == {
        **new_config,
        "billing": None,
    }


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
    json = response.json()
    assert json == {**config, "billing": None}


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


def test_user_config_billing_plan(client):
    """Ensure that we can get (but not write) billing plan in user config"""

    billing = {"plan": "business_monthly", "session_id": "foo"}
    asyncio.run(auth.add_user("biz_plan_user@nyrkio.com", "foo", billing=billing))

    client = AuthenticatedTestClient(app)
    client.email = "biz_plan_user@nyrkio.com"
    client.login()

    config = {
        "billing": billing,
    }
    response = client.get("/api/v0/user/config")
    assert response.status_code == 200

    json = response.json()
    assert "billing" in json
    assert json["billing"]["plan"] == billing["plan"]

    # It should not be possible to set the billing plan via the /config endpoint
    # because it's a read-only field.
    response = client.post("/api/v0/user/config", json=config)
    assert response.status_code == 400

    response = client.put("/api/v0/user/config", json=config)
    assert response.status_code == 400

    del config["billing"]
    response = client.put("/api/v0/user/config", json=config)
    assert response.status_code == 200
