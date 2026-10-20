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
