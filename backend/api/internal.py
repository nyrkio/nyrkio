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
from typing import Dict, Optional

from fastapi import APIRouter, Depends, Header, HTTPException

from backend.auth import auth
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


@internal_router.get("/account")
async def get_account(user: User = Depends(auth.current_active_user)) -> Dict:
    """The caller's account, for the switch to v3. No password hash, no OAuth tokens, no Slack data."""
    return {
        "id": str(user.id),
        "email": user.email,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "github_username": user.github_username,
        "is_cph_user": user.is_cph_user,
        "is_repo_owner": user.is_repo_owner,
        "billing": user.billing,
        "billing_runners": user.billing_runners,
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


@internal_router.get("/export")
async def get_export(user: User = Depends(auth.current_active_user)) -> Dict:
    """
    What the public v0 API cannot return, for the switch: the caller's disabled metrics, the pull
    request results and the pull request index (which test names each pull request has).
    """
    db = DBStore().db
    disabled: Dict[str, list] = {}
    async for row in db.metrics.find({"user_id": user.id}):
        disabled.setdefault(row["test_name"], []).append(row["metric_name"])

    keep_out = {"_id": 0, "user_id": 0, "version": 0, "meta": 0}
    pull_request_results = [
        doc
        async for doc in db.test_results.find(
            {"user_id": user.id, "pull_request": {"$exists": True}}, keep_out
        )
    ]
    pull_requests = [
        {
            "git_repo": row["git_repo"],
            "git_commit": row["git_commit"],
            "pull_number": row["pull_number"],
            "test_names": row.get("test_names", []),
        }
        async for row in db.pr_tests.find({"user_id": user.id})
    ]
    return {
        "disabled_metrics": disabled,
        "pull_request_results": pull_request_results,
        "pull_requests": pull_requests,
    }
