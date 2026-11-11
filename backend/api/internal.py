"""
Internal endpoints for the v3 backend during the soft launch.

They live outside /api/v0: the edge only forwards /api/v0/* (and /openapi*, webhooks)
to this backend, so these paths are not reachable from the internet. They are also left
out of the OpenAPI schema.

Every request must carry the shared secret in X-Internal-Token (INTERNAL_API_TOKEN, set
on v2 and v3). Without a matching secret the path answers 404, as if it did not exist.
The caller must also present its own bearer token, and gets back only that account; except the
stats, which a superuser asks for all accounts.
"""

import asyncio
import calendar
import hmac
import logging
import os
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional

import jwt
from bson import ObjectId
from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from fastapi_users import exceptions
from starlette.responses import JSONResponse

from backend.auth import auth
from backend.auth.common import SECRET
from backend.db.db import DBStore, User


def require_internal_secret(x_internal_token: Optional[str] = Header(default=None)):
    expected = os.environ.get("INTERNAL_API_TOKEN")
    if not expected or not x_internal_token:
        raise HTTPException(status_code=404, detail="Not Found")
    if not hmac.compare_digest(x_internal_token, expected):
        raise HTTPException(status_code=404, detail="Not Found")


# Route dependencies run before the endpoint's own, so a missing secret is 404, never 401.
internal_router = APIRouter(
    prefix="/internal/v2",
    include_in_schema=False,
    dependencies=[Depends(require_internal_secret)],
)


async def _installations(gh_ids) -> Dict[str, Dict]:
    """The GitHub App installations of these GitHub account ids, by id. The notifiers of v3 read them
    from its own table, so without them a switched account would stop getting GitHub issues."""
    store = DBStore()
    found = {}
    for gh_id in gh_ids:
        try:
            installation = await store.get_github_installation(gh_id)
        except (TypeError, ValueError):
            continue
        if installation:
            found[str(gh_id)] = {k: v for k, v in installation.items() if k != "_id"}
    return found


@internal_router.get("/account")
async def get_account(user: User = Depends(auth.current_active_user)) -> Dict:
    """The caller's account, for the switch to v3. No password hash and no OAuth tokens. What the user
    set up comes along, or it would stop working: the Slack connection (the webhook of the OAuth
    install), the GitHub token (PAT) that registers the user's runners and the GitHub App
    installations of the user's GitHub account. The captcha token comes too: a request for a new
    verification mail has to show the same one, and v3 checks it as v2 does."""
    github_ids = [
        a.account_id for a in (user.oauth_accounts or []) if a.oauth_name == "github"
    ]
    return {
        "id": str(user.id),
        "email": user.email,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "is_superuser": user.is_superuser,
        "captcha_token": user.captcha_token,
        "github_username": user.github_username,
        "is_cph_user": user.is_cph_user,
        "is_repo_owner": user.is_repo_owner,
        "billing": user.billing,
        "billing_runners": user.billing_runners,
        "slack": user.slack,
        "github_pat": await DBStore().get_pat(user.id),
        "github_installations": await _installations(github_ids),
        "oauth_accounts": [
            {
                "oauth_name": a.oauth_name,
                "account_id": a.account_id,
                "account_email": a.account_email,
                "organizations": a.organizations or [],
            }
            for a in (user.oauth_accounts or [])
        ],
    }


def _admin_org_id(user: User, login: str):
    """The id of the org `login` if the caller is an admin of it, else 403."""
    for account in user.oauth_accounts or []:
        for membership in account.organizations or []:
            org = membership.get("organization") or {}
            if org.get("login") == login and membership.get("role") == "admin":
                return org["id"]
    raise HTTPException(status_code=403, detail="Not an admin of this organization")


@internal_router.get("/email-taken")
async def email_taken(email: str) -> Dict:
    """
    Whether v2 has an account with this email. v3 asks before it registers a new user (NEW_USERS_HOME=v3): an
    email that v2 already has has to stay a v2 registration, or the account would exist twice and its switch
    would be refused. Only the secret is needed, because no account is read.
    """
    try:
        await auth.get_user_by_email(email)
    except exceptions.UserNotExists:
        return {"taken": False}
    return {"taken": True}


@internal_router.get("/export")
async def get_export(
    org: Optional[str] = None, user: User = Depends(auth.current_active_user)
) -> Dict:
    """
    What the public v0 API cannot return, for the switch: disabled metrics, the pull request
    results, the pull request index (which test names each pull request has) and every test name.
    Of the caller, or with org=<login> of an organization the caller administers.
    """
    owner = _admin_org_id(user, org) if org else user.id
    db = DBStore().db
    disabled: Dict[str, list] = {}
    async for row in db.metrics.find({"user_id": owner}):
        disabled.setdefault(row["test_name"], []).append(row["metric_name"])

    keep_out = {"_id": 0, "user_id": 0, "version": 0, "meta": 0}
    pull_request_results = [
        doc
        async for doc in db.test_results.find(
            {"user_id": owner, "pull_request": {"$exists": True}}, keep_out
        )
    ]
    pull_requests = [
        {
            "git_repo": row["git_repo"],
            "git_commit": row["git_commit"],
            "pull_number": row["pull_number"],
            "test_names": row.get("test_names", []),
        }
        async for row in db.pr_tests.find({"user_id": owner})
    ]
    export = {
        "disabled_metrics": disabled,
        "pull_request_results": pull_request_results,
        "pull_requests": pull_requests,
    }
    # Every test name. The public listing of the tests is a random sample, so it misses some. The
    # organization API serves only the names under "<login>/", so only those are listed for an org.
    names = await db.test_results.distinct("test_name", {"user_id": owner})
    export["test_names"] = sorted(
        n for n in names if not org or n.startswith(org + "/")
    )
    if org:
        export["github_installations"] = await _installations([owner])
    return export


async def _owner_names(db, ids: List) -> Dict[str, str]:
    """The email of each user and the login of each org among the owner ids of results (an org's id is a GitHub id)."""
    names = {}
    users = [i for i in ids if isinstance(i, ObjectId)]
    async for row in db.User.find({"_id": {"$in": users}}, {"email": 1}):
        names[str(row["_id"])] = row["email"]
    for org_id in (i for i in ids if isinstance(i, int)):
        row = await db.User.find_one(
            {"oauth_accounts.organizations.organization.id": org_id},
            {"oauth_accounts.organizations": 1},
        )
        for account in (row or {}).get("oauth_accounts", []):
            for member in account.get("organizations") or []:
                org = member.get("organization") or {}
                if org.get("id") == org_id:
                    names[str(org_id)] = org.get("login")
    return names


@internal_router.get("/stats")
async def get_stats(
    since: datetime,
    until: datetime,
    limit: int = Query(20, ge=1, le=100),
    user: User = Depends(auth.current_active_superuser),
) -> Dict:
    """
    What was uploaded in [since, until), for the admin dashboard of v3: totals, uploads per day and the
    busiest accounts. Counted by the time a result was stored (meta.last_modified), not the time of the
    benchmark. Results from before meta existed are not counted. The scan wants an index on
    test_results.meta.last_modified (see the rollout runbook).
    """
    db = DBStore().db
    is_pr = {"$cond": [{"$ifNull": ["$pull_request", False]}, 1, 0]}
    day = {"$dateToString": {"format": "%Y-%m-%d", "date": "$meta.last_modified"}}
    pipeline = [
        {"$match": {"meta.last_modified": {"$gte": since, "$lt": until}}},
        {
            "$facet": {
                "accounts": [
                    {
                        "$group": {
                            "_id": "$user_id",
                            "uploads": {"$sum": 1},
                            "pr_uploads": {"$sum": is_pr},
                            "tests": {"$addToSet": "$test_name"},
                            "last_upload": {"$max": "$meta.last_modified"},
                        }
                    }
                ],
                "days": [
                    {
                        "$group": {
                            "_id": day,
                            "uploads": {"$sum": 1},
                            "pr_uploads": {"$sum": is_pr},
                        }
                    },
                    {"$sort": {"_id": 1}},
                ],
            }
        },
    ]
    found = (await db.test_results.aggregate(pipeline).to_list(1))[0]
    accounts = sorted(found["accounts"], key=lambda a: -a["uploads"])
    names = await _owner_names(db, [a["_id"] for a in accounts[:limit]])
    top = []
    for a in accounts[:limit]:
        top.append(
            {
                "id": str(a["_id"]),
                "name": names.get(str(a["_id"])),
                "org": isinstance(a["_id"], int),
                "uploads": a["uploads"],
                "pr_uploads": a["pr_uploads"],
                "tests": len(a["tests"]),
                "last_upload": a["last_upload"],
                "total_results": await db.test_results.count_documents(
                    {"user_id": a["_id"]}
                ),
            }
        )
    return {
        "uploads": sum(a["uploads"] for a in accounts),
        "pr_uploads": sum(a["pr_uploads"] for a in accounts),
        "active_accounts": [
            str(a["_id"]) for a in accounts if not isinstance(a["_id"], int)
        ],
        "active_orgs": [str(a["_id"]) for a in accounts if isinstance(a["_id"], int)],
        "tests": sum(len(a["tests"]) for a in accounts),
        "accounts_total": await db.User.count_documents({}),
        "new_accounts": await db.User.count_documents(
            {
                "_id": {
                    "$gte": ObjectId.from_datetime(since),
                    "$lt": ObjectId.from_datetime(until),
                }
            }
        ),
        "days": [
            {"day": d["_id"], "uploads": d["uploads"], "pr_uploads": d["pr_uploads"]}
            for d in found["days"]
        ],
        "top": top,
    }


@internal_router.get("/stats/recent")
async def get_recent_uploads(
    since: datetime,
    limit: int = Query(50, ge=1, le=200),
    user: User = Depends(auth.current_active_superuser),
) -> List[Dict]:
    """The latest uploads after `since`, newest first, for the live view of the admin dashboard."""
    db = DBStore().db
    keep = {
        "user_id": 1,
        "test_name": 1,
        "pull_request": 1,
        "meta.last_modified": 1,
        "attributes.git_repo": 1,
        "attributes.branch": 1,
    }
    rows = (
        await db.test_results.find({"meta.last_modified": {"$gt": since}}, keep)
        .sort("meta.last_modified", -1)
        .limit(limit)
        .to_list(None)
    )
    names = await _owner_names(db, list({r["user_id"] for r in rows}))
    return [
        {
            "at": r["meta"]["last_modified"],
            "account_id": str(r["user_id"]),
            "account": names.get(str(r["user_id"])),
            "test": r["test_name"],
            "repo": r.get("attributes", {}).get("git_repo"),
            "branch": r.get("attributes", {}).get("branch"),
            "pull_request": r.get("pull_request"),
        }
        for r in rows
    ]


# The accounts report reads the whole results collection, which takes minutes on prod, so it is built in
# the background and kept for a few hours. The next call after that, or one with refresh, builds it again.
ACTIVE_MONTHS = 3
REPORT_TTL = 6 * 3600
REPORT_CONCURRENCY = 4
_report: Dict = {
    "at": None,
    "since": None,
    "accounts": None,
    "task": None,
    "error": None,
}


def _months_ago(now: datetime, months: int) -> datetime:
    month = now.month - months
    year = now.year + (month - 1) // 12
    month = (month - 1) % 12 + 1
    return now.replace(
        year=year, month=month, day=min(now.day, calendar.monthrange(year, month)[1])
    )


async def _account_rows(db, since: datetime) -> List[Dict]:
    """
    One row per account with what the report counts. Activity is an upload, a settings edit or runner usage
    since `since`: v2 does not record logins. A dashboard is a result that is not the demo data every new
    account is given, and is not a pull request result; an org's counts for its members.
    """
    demo = await db.default_data.distinct("test_name")
    own_data = {"$nin": demo}
    sem = asyncio.Semaphore(REPORT_CONCURRENCY)

    async def has_history(owner) -> bool:
        async with sem:
            found = await db.test_results.find_one(
                {
                    "user_id": owner,
                    "pull_request": {"$exists": False},
                    "test_name": own_data,
                },
                {"_id": 1},
            )
            return found is not None

    owners = await db.test_results.distinct("user_id")
    with_history = {
        str(o)
        for o, has in zip(owners, await asyncio.gather(*map(has_history, owners)))
        if has
    }
    since_iso = since.replace(tzinfo=None).isoformat()
    uploaded = {
        str(r["_id"])
        async for r in db.test_results.aggregate(
            [
                {
                    "$match": {
                        "meta.last_modified": {"$gte": since},
                        "test_name": own_data,
                    }
                },
                {"$group": {"_id": "$user_id"}},
            ],
            allowDiskUse=True,
        )
    }
    edited = {
        str(r["user_id"])
        async for r in db.user_config.find(
            {
                "$or": [
                    {"meta.last_modified": {"$gte": since_iso}},
                    {"meta.last_modified": {"$gte": since}},
                ]
            },
            {"user_id": 1},
        )
    }
    used_runners = {
        str(v)
        for v in await db.runner_usage_raw.distinct(
            "plan_info.nyrkio_user_id", {"report_aws_timestamp": {"$gte": since_iso}}
        )
    }

    rows = []
    keep = {
        "is_verified": 1,
        "oauth_accounts.organizations.organization.id": 1,
        "oauth_accounts.organizations.role": 1,
    }
    async for u in db.User.find({}, keep):
        orgs = [
            (str(m["organization"]["id"]), m.get("role"))
            for a in u.get("oauth_accounts") or []
            for m in a.get("organizations") or []
            if (m.get("organization") or {}).get("id") is not None
        ]
        uid = str(u["_id"])
        rows.append(
            {
                "id": uid,
                "verified": bool(u.get("is_verified")),
                "active": uid in uploaded or uid in edited or uid in used_runners,
                "org_active": any(o in uploaded for o, _ in orgs),
                "own": uid in with_history,
                "org_member": any(o in with_history for o, _ in orgs),
                "org_admin": any(r == "admin" and o in with_history for o, r in orgs),
            }
        )
    return rows


async def _build_report():
    since = _months_ago(datetime.now(timezone.utc), ACTIVE_MONTHS)
    try:
        rows = await _account_rows(DBStore().db, since)
    except Exception as e:
        _report["error"] = type(e).__name__
        logging.error(f"The accounts report failed: {e!r}")
        return
    _report.update(
        at=datetime.now(timezone.utc), since=since, accounts=rows, error=None
    )


@internal_router.get("/stats/accounts")
async def get_account_report(
    refresh: bool = False, user: User = Depends(auth.current_active_superuser)
) -> Dict:
    """
    The accounts for the admin dashboard of v3, one row each (no emails): verified, active in the last
    three months, with a dashboard of their own or of an org. `status` is ready, computing (`accounts`
    then holds the previous report, if any) or failed.
    """
    now = datetime.now(timezone.utc)
    running = _report["task"] is not None and not _report["task"].done()
    stale = _report["at"] is None or (now - _report["at"]).total_seconds() > REPORT_TTL
    if not running and (refresh or (stale and not _report["error"])):
        _report["error"] = None
        _report["task"] = asyncio.create_task(_build_report())
        running = True
    status = "computing" if running else "failed" if _report["error"] else "ready"
    return {
        "status": status,
        "error": _report["error"],
        "computed_at": _report["at"],
        "since": _report["since"],
        "accounts": _report["accounts"],
    }


# The write freeze closes the window at the end of a switch: v3 freezes the account's writes, copies
# once more, and then serves the account itself. The freeze expires on its own, so a switch that dies
# cannot lock an account out.
FREEZE_SECONDS = 120


def _freeze_key(user: User, org: Optional[str]) -> str:
    if org:
        _admin_org_id(user, org)
        return f"org:{org}"
    return str(user.id)


@internal_router.post("/freeze")
async def freeze(
    org: Optional[str] = None, user: User = Depends(auth.current_active_user)
) -> Dict:
    until = time.time() + FREEZE_SECONDS
    await DBStore().db.switch_freeze.update_one(
        {"_id": _freeze_key(user, org)}, {"$set": {"until": until}}, upsert=True
    )
    return {"until": until}


@internal_router.delete("/freeze")
async def unfreeze(
    org: Optional[str] = None, user: User = Depends(auth.current_active_user)
) -> Dict:
    await DBStore().db.switch_freeze.delete_one({"_id": _freeze_key(user, org)})
    return {}


def _token_subject(request: Request) -> Optional[str]:
    token = None
    authorization = request.headers.get("authorization", "")
    if authorization.lower().startswith("bearer "):
        token = authorization[len("bearer ") :].strip()
    token = token or request.cookies.get("auth_session")
    if not token:
        return None
    try:
        payload = jwt.decode(
            token, SECRET, algorithms=["HS256"], audience="fastapi-users:auth"
        )
    except jwt.PyJWTError:
        return None
    return payload.get("sub")


def _org_login_in_path(path: str) -> Optional[str]:
    """The organization a write under /api/v0/orgs is about, from its path."""
    rest = path[len("/api/v0/orgs") :].lstrip("/")
    for prefix in ("result/", "config/", "org/", "pulls/"):
        if rest.startswith(prefix):
            return rest[len(prefix) :].split("/")[0]
    return None


# POST endpoints that only read: the body names the tests to read. The switch job itself calls them
# while the account is frozen.
READ_ONLY_POSTS = ("/results/bulk", "/results/changes/bulk")


def _is_write(request: Request) -> bool:
    if request.method in ("GET", "HEAD", "OPTIONS"):
        return False
    return not request.url.path.endswith(READ_ONLY_POSTS)


async def switch_freeze_middleware(request: Request, call_next):
    """Writes of a frozen account or organization answer 503 with Retry-After until the freeze ends."""
    path = request.url.path
    if _is_write(request) and path.startswith("/api/v0/"):
        keys = []
        subject = _token_subject(request)
        if subject:
            keys.append(subject)
        if path.startswith("/api/v0/orgs/"):
            login = _org_login_in_path(path)
            if login:
                keys.append(f"org:{login}")
        for key in keys:
            row = await DBStore().db.switch_freeze.find_one({"_id": key})
            if row and row["until"] > time.time():
                return JSONResponse(
                    {"detail": "This account is being moved, retry in a moment"},
                    status_code=503,
                    headers={"Retry-After": "5"},
                )
    return await call_next(request)
