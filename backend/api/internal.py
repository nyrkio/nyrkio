"""
Internal endpoints for the v3 backend during the soft launch.

They live outside /api/v0: the edge only forwards /api/v0/* (and /openapi*, webhooks)
to this backend, so these paths are not reachable from the internet. They are also left
out of the OpenAPI schema.

Every request must carry the shared secret in X-Internal-Token (INTERNAL_API_TOKEN, set
on v2 and v3). Without a matching secret the path answers 404, as if it did not exist.
The caller must also present its own bearer token, and gets back only that account.
"""

import hmac
import os
import time
from typing import Dict, Optional

import jwt
from fastapi import APIRouter, Depends, Header, HTTPException, Request
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
    installations of the user's GitHub account."""
    github_ids = [
        a.account_id for a in (user.oauth_accounts or []) if a.oauth_name == "github"
    ]
    return {
        "id": str(user.id),
        "email": user.email,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "is_superuser": user.is_superuser,
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
