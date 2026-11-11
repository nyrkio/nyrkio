import asyncio
import time
from datetime import datetime, timedelta, timezone

import pytest

from backend.api import internal as internal_api
from backend.db.db import DBStore

SECRET = "test-internal-secret"
STATS = "/internal/v2/stats"
RECENT = "/internal/v2/stats/recent"
DOC = {
    "timestamp": 1,
    "metrics": [{"name": "m1", "value": 1.0, "unit": "ms"}],
    "attributes": {
        "git_repo": "https://github.com/a/b",
        "branch": "main",
        "git_commit": "c1",
    },
}


def _doc(n):
    return {
        **DOC,
        "timestamp": n,
        "attributes": {**DOC["attributes"], "git_commit": f"c{n}"},
    }


def _window(hours_before=1, hours_after=1):
    now = datetime.now(timezone.utc)
    return {
        "since": (now - timedelta(hours=hours_before)).isoformat(),
        "until": (now + timedelta(hours=hours_after)).isoformat(),
    }


@pytest.fixture
def internal_headers(superuser_client, monkeypatch):
    monkeypatch.setenv("INTERNAL_API_TOKEN", SECRET)
    superuser_client.login()
    return {**superuser_client.get_headers(), "X-Internal-Token": SECRET}


@pytest.fixture
def internal(superuser_client, monkeypatch):
    monkeypatch.setenv("INTERNAL_API_TOKEN", SECRET)
    superuser_client.login()
    return {**superuser_client.get_headers(), "X-Internal-Token": SECRET}


def test_stats_are_hidden_without_the_secret(superuser_client, monkeypatch):
    monkeypatch.setenv("INTERNAL_API_TOKEN", SECRET)
    superuser_client.login()
    assert superuser_client.get(STATS, params=_window()).status_code == 404
    assert (
        superuser_client.get(RECENT, params={"since": "2020-01-01"}).status_code == 404
    )


def test_stats_are_for_superusers(client, monkeypatch):
    monkeypatch.setenv("INTERNAL_API_TOKEN", SECRET)
    client.login()
    headers = {**client.get_headers(), "X-Internal-Token": SECRET}
    assert (
        client.request("GET", STATS, headers=headers, params=_window()).status_code
        == 403
    )
    assert (
        client.request(
            "GET", RECENT, headers=headers, params={"since": "2020-01-01"}
        ).status_code
        == 403
    )


def _stats(client, headers, **params):
    return client.request(
        "GET", STATS, headers=headers, params={**_window(), "limit": 100, **params}
    ).json()


def _admin(stats):
    zero = {"uploads": 0, "pr_uploads": 0, "tests": 0, "total_results": 0}
    return next((a for a in stats["top"] if a["name"] == "admin@foo.com"), zero)


def test_stats_count_uploads_of_the_period(superuser_client, internal):
    # the test database holds some results of its own: compare with the state before
    before = _stats(superuser_client, internal)
    for n in (1, 2):
        assert (
            superuser_client.post("/api/v0/result/stats/a", json=[_doc(n)]).status_code
            == 200
        )
    assert (
        superuser_client.post("/api/v0/result/stats/b", json=[_doc(3)]).status_code
        == 200
    )
    pr = superuser_client.post("/api/v0/pulls/a/b/5/result/stats/a", json=[_doc(4)])
    assert pr.status_code == 200

    after = _stats(superuser_client, internal)
    assert after["uploads"] - before["uploads"] == 4
    assert after["pr_uploads"] - before["pr_uploads"] == 1
    assert after["tests"] - before["tests"] == 2
    assert sum(d["uploads"] for d in after["days"]) == after["uploads"]
    assert after["accounts_total"] >= 1 and after["new_accounts"] >= 0
    top = _admin(after)
    assert top["org"] is False
    for key in ("uploads", "pr_uploads", "tests", "total_results"):
        assert (
            top[key] - _admin(before)[key]
            == {"uploads": 4, "pr_uploads": 1, "tests": 2, "total_results": 4}[key]
        )
    assert after["top"] == sorted(after["top"], key=lambda a: -a["uploads"])


def test_stats_of_a_period_without_uploads_are_empty(superuser_client, internal):
    assert (
        superuser_client.post("/api/v0/result/stats/a", json=[DOC]).status_code == 200
    )
    past = {"since": "2020-01-01T00:00:00+00:00", "until": "2020-02-01T00:00:00+00:00"}
    stats = superuser_client.request("GET", STATS, headers=internal, params=past).json()
    assert (
        stats["uploads"],
        stats["active_accounts"],
        stats["active_orgs"],
        stats["top"],
        stats["days"],
    ) == (0, [], [], [], [])


def test_stats_limit_the_top_list(superuser_client, internal):
    assert (
        superuser_client.post("/api/v0/result/stats/a", json=[DOC]).status_code == 200
    )
    stats = superuser_client.request(
        "GET", STATS, headers=internal, params={**_window(), "limit": 1}
    ).json()
    assert len(stats["top"]) == 1
    bad = superuser_client.request(
        "GET", STATS, headers=internal, params={**_window(), "limit": 0}
    )
    assert bad.status_code == 422


def test_recent_uploads_newest_first_after_since(superuser_client, internal):
    for n in (1, 2, 3):
        assert (
            superuser_client.post(
                f"/api/v0/result/stats/t{n}", json=[_doc(n)]
            ).status_code
            == 200
        )
    since = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    rows = superuser_client.request(
        "GET", RECENT, headers=internal, params={"since": since, "limit": 2}
    ).json()
    assert [r["test"] for r in rows] == ["stats/t3", "stats/t2"]
    assert rows[0]["account"] == "admin@foo.com"
    assert rows[0]["repo"] == "https://github.com/a/b" and rows[0]["branch"] == "main"
    assert rows[0]["pull_request"] is None

    later = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    assert (
        superuser_client.request(
            "GET", RECENT, headers=internal, params={"since": later}
        ).json()
        == []
    )


def test_stats_name_an_org_by_its_login(superuser_client, internal):
    """The owner of an org's results is the GitHub id of the org; a membership may lack the organization."""
    db = DBStore().db
    users = db.User
    before = asyncio.run(users.find_one({"email": "admin@foo.com"}))["oauth_accounts"]
    members = [
        {"role": "member", "user": {"login": "someone"}},
        {"role": "admin", "organization": {"id": 4242, "login": "acme"}},
    ]
    account = {
        "oauth_name": "github",
        "account_id": "1",
        "account_email": "a@foo.com",
        "access_token": "unused",
        "organizations": members,
    }
    asyncio.run(
        users.update_one(
            {"email": "admin@foo.com"}, {"$set": {"oauth_accounts": [account]}}
        )
    )
    doc = {
        "_id": {"org": 4242, "timestamp": 1},
        "user_id": 4242,
        "test_name": "acme/repo/main/t",
        "timestamp": 1,
        "attributes": DOC["attributes"],
        "meta": {"last_modified": datetime.now(timezone.utc)},
    }
    asyncio.run(db.test_results.insert_one(doc))
    try:
        stats = _stats(superuser_client, internal)
        [org] = [a for a in stats["top"] if a["id"] == "4242"]
        assert (org["org"], org["name"]) == (True, "acme")
        assert "4242" in stats["active_orgs"]
        rows = superuser_client.request(
            "GET",
            RECENT,
            headers=internal,
            params={"since": _window()["since"], "limit": 200},
        ).json()
        assert [r["account"] for r in rows if r["account_id"] == "4242"] == ["acme"]
    finally:
        asyncio.run(db.test_results.delete_one({"_id": doc["_id"]}))
        asyncio.run(
            users.update_one(
                {"email": "admin@foo.com"}, {"$set": {"oauth_accounts": before}}
            )
        )


REPORT = "/internal/v2/stats/accounts"
ROW_KEYS = {"id", "verified", "active", "org_active", "own", "org_member", "org_admin"}


@pytest.fixture
def fresh_report():
    reset = dict(at=None, since=None, accounts=None, task=None, error=None)
    internal_api._report.update(reset)
    yield
    internal_api._report.update(reset)


def _ask(client, headers, **params):
    return client.request("GET", REPORT, headers=headers, params=params).json()


def _built(client, headers, **params):
    """The report builds in the background: ask until it is not computing."""
    for _ in range(100):
        body = _ask(client, headers, **params)
        if body["status"] != "computing":
            return body
        params = {}
        time.sleep(0.1)
    raise AssertionError("still computing")


def _account_id(email):
    return str(asyncio.run(DBStore().db.User.find_one({"email": email}))["_id"])


def test_account_report_is_for_superusers(client, monkeypatch, fresh_report):
    monkeypatch.setenv("INTERNAL_API_TOKEN", SECRET)
    client.login()
    headers = {**client.get_headers(), "X-Internal-Token": SECRET}
    assert client.request("GET", REPORT, headers=headers).status_code == 403


def test_account_report_builds_in_the_background(
    superuser_client, internal_headers, fresh_report
):
    superuser_client.login()
    assert (
        superuser_client.post("/api/v0/result/report/a", json=[DOC]).status_code == 200
    )

    first = _ask(superuser_client, internal_headers)
    assert (first["status"], first["accounts"], first["computed_at"]) == (
        "computing",
        None,
        None,
    )
    report = _built(superuser_client, internal_headers)
    assert report["status"] == "ready" and report["computed_at"] and report["since"]

    rows = {r["id"]: r for r in report["accounts"]}
    assert all(set(r) == ROW_KEYS for r in rows.values())
    # an upload of its own is a dashboard and activity; the demo data every account is given is neither
    mine = rows[_account_id("admin@foo.com")]
    assert (mine["own"], mine["active"], mine["verified"]) == (True, True, True)
    other = rows[_account_id("john@foo.com")]
    assert (other["own"], other["active"]) == (False, False)


def test_account_report_is_kept_until_refreshed(
    superuser_client, internal_headers, monkeypatch, fresh_report
):
    calls = []

    async def rows(db, since):
        calls.append(since)
        return [{"id": "x"}]

    monkeypatch.setattr(internal_api, "_account_rows", rows)
    superuser_client.login()
    assert _built(superuser_client, internal_headers)["accounts"] == [{"id": "x"}]
    assert _built(superuser_client, internal_headers)["status"] == "ready"
    assert len(calls) == 1
    # a refresh answers with the previous report while it builds the next
    again = _ask(superuser_client, internal_headers, refresh="true")
    assert (again["status"], again["accounts"]) == ("computing", [{"id": "x"}])
    assert _built(superuser_client, internal_headers)["status"] == "ready"
    assert len(calls) == 2
    # a report that is too old is built again
    internal_api._report["at"] -= timedelta(seconds=internal_api.REPORT_TTL + 1)
    assert _built(superuser_client, internal_headers)["status"] == "ready"
    assert len(calls) == 3


def test_a_failed_account_report_is_not_retried_until_asked(
    superuser_client, internal_headers, monkeypatch, fresh_report
):
    outcome = {"fail": True}
    calls = []

    async def rows(db, since):
        calls.append(1)
        if outcome["fail"]:
            raise RuntimeError("no database")
        return []

    monkeypatch.setattr(internal_api, "_account_rows", rows)
    superuser_client.login()
    report = _built(superuser_client, internal_headers)
    assert (report["status"], report["error"]) == ("failed", "RuntimeError")
    assert _ask(superuser_client, internal_headers)["status"] == "failed"
    assert len(calls) == 1
    outcome["fail"] = False
    assert (
        _built(superuser_client, internal_headers, refresh="true")["status"] == "ready"
    )
    assert len(calls) == 2


def test_the_report_looks_back_whole_months():
    at = datetime(2026, 11, 11, tzinfo=timezone.utc)
    assert internal_api._months_ago(at, 3) == datetime(2026, 8, 11, tzinfo=timezone.utc)
    assert internal_api._months_ago(
        datetime(2026, 3, 31, tzinfo=timezone.utc), 1
    ) == datetime(2026, 2, 28, tzinfo=timezone.utc)
    assert internal_api._months_ago(
        datetime(2026, 2, 15, tzinfo=timezone.utc), 3
    ) == datetime(2025, 11, 15, tzinfo=timezone.utc)
    assert internal_api._months_ago(
        datetime(2026, 3, 15, tzinfo=timezone.utc), 3
    ) == datetime(2025, 12, 15, tzinfo=timezone.utc)
