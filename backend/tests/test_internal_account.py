SECRET = "test-internal-secret"
PATH = "/internal/v2/account"


def test_hidden_when_no_secret_is_configured(client, monkeypatch):
    monkeypatch.delenv("INTERNAL_API_TOKEN", raising=False)
    client.login()
    assert client.get(PATH).status_code == 404


def test_hidden_with_wrong_or_missing_secret(client, monkeypatch):
    monkeypatch.setenv("INTERNAL_API_TOKEN", SECRET)
    client.login()
    assert client.get(PATH).status_code == 404
    response = client.request("GET", PATH, headers={"X-Internal-Token": "wrong"})
    assert response.status_code == 404


def test_secret_without_user_token_is_rejected(unauthenticated_client, monkeypatch):
    monkeypatch.setenv("INTERNAL_API_TOKEN", SECRET)
    response = unauthenticated_client.get(PATH, headers={"X-Internal-Token": SECRET})
    assert response.status_code == 401


def test_returns_own_account_without_secrets(client, monkeypatch):
    monkeypatch.setenv("INTERNAL_API_TOKEN", SECRET)
    client.login()
    headers = {**client.get_headers(), "X-Internal-Token": SECRET}
    response = client.request("GET", PATH, headers=headers)
    assert response.status_code == 200
    account = response.json()
    assert account["email"] == "john@foo.com"
    assert "hashed_password" not in account
    for oauth in account["oauth_accounts"]:
        assert "access_token" not in oauth
        assert "refresh_token" not in oauth


EXPORT = "/internal/v2/export"
DOC = {
    "timestamp": 1,
    "metrics": [{"name": "m1", "value": 1.0, "unit": "ms"}],
    "attributes": {
        "git_repo": "https://github.com/a/b",
        "branch": "main",
        "git_commit": "c1",
    },
}


def test_export_is_hidden_without_the_secret(client, monkeypatch):
    monkeypatch.setenv("INTERNAL_API_TOKEN", SECRET)
    client.login()
    assert client.get(EXPORT).status_code == 404


def test_export_has_disabled_metrics_and_pull_requests(client, monkeypatch):
    monkeypatch.setenv("INTERNAL_API_TOKEN", SECRET)
    client.login()
    assert client.post("/api/v0/result/bench/a", json=[DOC]).status_code == 200
    r = client.post("/api/v0/result/bench/a/changes/disable", json=["m1"])
    assert r.status_code == 200
    pr = {
        **DOC,
        "timestamp": 2,
        "attributes": {**DOC["attributes"], "git_commit": "c2"},
    }
    r = client.post("/api/v0/pulls/a/b/5/result/bench/a", json=[pr])
    assert r.status_code == 200

    headers = {**client.get_headers(), "X-Internal-Token": SECRET}
    export = client.request("GET", EXPORT, headers=headers).json()
    assert export["disabled_metrics"] == {"bench/a": ["m1"]}
    assert [d["pull_request"] for d in export["pull_request_results"]] == [5]
    assert export["pull_request_results"][0]["test_name"] == "bench/a"
    assert export["pull_requests"] == [
        {
            "git_repo": "a/b",
            "git_commit": "c2",
            "pull_number": 5,
            "test_names": ["bench/a"],
        }
    ]
    for doc in export["pull_request_results"]:
        assert "user_id" not in doc and "meta" not in doc


def test_freeze_blocks_writes_of_the_account_until_released(client, monkeypatch):
    monkeypatch.setenv("INTERNAL_API_TOKEN", SECRET)
    client.login()
    internal = {**client.get_headers(), "X-Internal-Token": SECRET}
    assert (
        client.request("POST", "/internal/v2/freeze", headers=internal).status_code
        == 200
    )

    blocked = client.post("/api/v0/result/bench/frozen", json=[DOC])
    assert blocked.status_code == 503
    assert blocked.headers["retry-after"] == "5"
    # reads still work
    assert client.get("/api/v0/results").status_code == 200

    assert (
        client.request("DELETE", "/internal/v2/freeze", headers=internal).status_code
        == 200
    )
    assert client.post("/api/v0/result/bench/frozen", json=[DOC]).status_code == 200


def test_freeze_expires_by_itself(client, monkeypatch):
    import time as _time

    monkeypatch.setenv("INTERNAL_API_TOKEN", SECRET)
    client.login()
    internal = {**client.get_headers(), "X-Internal-Token": SECRET}
    client.request("POST", "/internal/v2/freeze", headers=internal)
    real = _time.time
    monkeypatch.setattr("backend.api.internal.time.time", lambda: real() + 600)
    assert client.post("/api/v0/result/bench/late", json=[DOC]).status_code == 200
