# Copyright (c) 2024, Nyrkiö Oy
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Union
import logging
import sys


from fastapi import FastAPI, APIRouter, Depends, HTTPException

from backend.auth import auth
from backend.auth import challenge_publish
from backend.api.admin import admin_router
from backend.api.billing import billing_router
from backend.api.changes import calc_changes
from backend.api.config import config_router
from backend.api.model import TestResults
from backend.api.organization import org_router
from backend.api.public import public_router
from backend.api.pull_request import pr_router
from backend.api.user import user_router
from backend.github.marketplace import market_router
from backend.db.db import (
    DBStoreMissingRequiredKeys,
    DBStoreResultExists,
    User,
    DBStore,
)
from backend.notifiers.slack import SlackNotifier
from backend.notifiers.github import GitHubIssueNotifier
from backend.api.background import precompute_cached_change_points
from backend.db.list_changes import change_points_per_commit

from fastapi.exceptions import RequestValidationError
from backend.api.pydantic_exception_handlers import (
    request_validation_exception_handler,
    http_exception_handler,
    unhandled_exception_handler,
)
from backend.api.pydantic_middleware import log_request_middleware

app = FastAPI(openapi_url="/openapi.json")

app.middleware("http")(log_request_middleware)
app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)


logging_out = logging.StreamHandler(stream=sys.stdout)
logging_out.setLevel(logging.INFO)
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(logging_out)

api_router = APIRouter()


# New 2025-05-01, trying not to overload /result/arbitrary path/additional_paths
@api_router.get("/changes/perCommit/{test_name_prefix:path}")
async def changes_per_commit(
    test_name_prefix: str,
    commit: str = None,
    user: User = Depends(auth.current_active_user),
):
    return await change_points_per_commit(user.id, test_name_prefix, commit)


@api_router.post("/result/{test_name:path}/changes/enable")
async def enable_changes(
    test_name: str,
    user: User = Depends(auth.current_active_user),
    metrics: List[str] = [],
):
    store = DBStore()
    await store.enable_changes(user.id, test_name, metrics)
    return {}


@api_router.post("/result/{test_name:path}/changes/disable")
async def disable_changes(
    test_name: str,
    user: User = Depends(auth.current_active_user),
    metrics: List[str] = [],
):
    if not metrics:
        raise HTTPException(
            status_code=400, detail="No metrics to disable change detection for"
        )
    store = DBStore()
    await store.disable_changes(user.id, test_name, metrics)
    return {}


@api_router.get("/result/{test_name:path}/changes")
async def changes(
    test_name: str,
    notify: Union[int, None] = None,
    user: User = Depends(auth.current_active_user),
):
    store = DBStore()
    config, config_meta = await store.get_user_config(user.id)

    public_base_url = None
    public_test_objects, public_test_objects_meta = await store.get_public_results(
        user.id
    )
    # print(public_test_objects)
    if public_test_objects:
        public_base_url = "https://nyrkio.com/public/"
    public_test_names = [entry["test_name"] for entry in public_test_objects]
    notifiers = await get_notifiers(
        notify,
        config,
        user,
        public_tests=public_test_names,
        public_base_url=public_base_url,
    )
    return await calc_changes(test_name, user.id, notifiers)


@api_router.get("/result/{test_name_prefix:path}/summary")
async def get_subtree_summary(
    test_name_prefix: str, user: User = Depends(auth.current_active_user)
) -> Dict:
    """
    Get all change points for all test results that are in the sub-tree of `test_name_prefix` and
    return a summary of that data.

    The UI would use this information to show something like "project: 57 change points, the latest
    on 2024-04-20".

    Note that for this feature we have added pre-computation and storage of change points.
    Without such pre-compute, we would here constantly be re-computing all test results of the user!
    """
    store = DBStore()
    cache = await store.get_summaries_cache(user.id)
    if test_name_prefix in cache:
        return cache[test_name_prefix]

    raise HTTPException(
        status_code=404,
        detail="Not Found: test_name_prefix={} user.id={}".format(
            test_name_prefix, user.id
        ),
    )


@api_router.get("/result/summarySiblings")
async def get_subtree_summary_siblings_root(
    user: User = Depends(auth.current_active_user),
) -> Dict:
    """
    Special case for getting all summarySiblings for the root of the tree.
    """
    store = DBStore()
    cache = await store.get_summaries_cache(user.id)
    if cache:
        return cache

    raise HTTPException(status_code=404, detail="Not Found")


@api_router.get("/result/{parent_test_name_prefix:path}/summarySiblings")
async def get_subtree_summary_siblings(
    parent_test_name_prefix: str, user: User = Depends(auth.current_active_user)
) -> Dict:
    """
    Like /summary but client will ask for the parent prefix, and we return all children of that parent.
    This allows a single call to replace separate HTTP calls for each list entry.
    """
    store = DBStore()
    cache = await store.get_summaries_cache(user.id)
    children = {}
    length = len(parent_test_name_prefix)
    for k, v in cache.items():
        if (
            len(k) > length
            and k[:length] == parent_test_name_prefix
            and k[length] == "/"
            and "/" not in k[length + 1 :]
        ):
            children[k] = v

    if children:
        return children

    raise HTTPException(
        status_code=404,
        detail="Not Found (summarySiblings, no children for {})".format(
            parent_test_name_prefix
        ),
    )


@api_router.get("/results/precompute")
async def precompute(user: User = Depends(auth.current_active_superuser)):
    print("Background task: precompute change points")
    await precompute_cached_change_points()
    return []


@api_router.get("/results")
async def results(user: User = Depends(auth.current_active_user)) -> List[Dict]:
    store = DBStore()
    results = await store.get_test_names(user.id)
    return [{"test_name": name} for name in results]


@api_router.delete("/results")
async def delete_results(user: User = Depends(auth.current_active_user)) -> List:
    store = DBStore()
    await store.delete_all_results(user)
    return []


@api_router.get("/result/{test_name:path}")
async def get_result(
    test_name: str, user: User = Depends(auth.current_active_user)
) -> List[Dict]:
    store = DBStore()
    test_names = await store.get_test_names(user.id)

    if not list(filter(lambda name: name == test_name, test_names)):
        raise HTTPException(status_code=404, detail="Not Found")

    results, _ = await store.get_results(user.id, test_name)

    return results


@api_router.delete("/result/{test_name:path}")
async def delete_result(
    test_name: str,
    timestamp: Union[int, None] = None,
    user: User = Depends(auth.current_active_user),
) -> List[Dict]:
    store = DBStore()
    test_names = await store.get_test_names(user.id)

    if not list(filter(lambda name: name == test_name, test_names)):
        raise HTTPException(status_code=404, detail="Not Found")

    await store.delete_result(user.id, test_name, timestamp)
    return []


@api_router.post("/result/{test_name:path}")
async def add_result(
    test_name: str, data: TestResults, user: User = Depends(auth.current_active_user)
):
    store = DBStore()

    try:
        await store.add_results(user.id, test_name, data.root)
    except DBStoreResultExists as e:
        explanation = {
            "reason": "Result already exists for key",
            "data": e.key,
        }
        raise HTTPException(status_code=400, detail=explanation)
    except DBStoreMissingRequiredKeys as e:
        explanation = {
            "reason": "Result is missing required keys",
            "data": e.missing_keys,
        }
        raise HTTPException(status_code=400, detail=explanation)

    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Invalid data")

    # Compute the change points and persist the result so they are cheap to GET later.
    # Since we compute them after POSTing them, may as well return the results to the user.
    return await changes(test_name, notify=1, user=user)


@api_router.put("/result/{test_name:path}")
async def update_result(
    test_name: str, data: TestResults, user: User = Depends(auth.current_active_user)
):
    store = DBStore()

    try:
        await store.add_results(user.id, test_name, data.root, update=True)
    except DBStoreMissingRequiredKeys as e:
        explanation = {
            "reason": "Result is missing required keys",
            "data": e.missing_keys,
        }
        raise HTTPException(status_code=400, detail=explanation)

    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Invalid data")

    # Compute the change points and persist the result so they are cheap to GET later.
    # Since we compute them after POSTing them, may as well return the results to the user.
    return await changes(test_name, notify=1, user=user)


@api_router.get("/default/results")
async def default_results() -> List[str]:
    store = DBStore()
    return await store.get_default_test_names()


@api_router.get("/default/result/{test_name}")
async def default_result(test_name: str) -> List[Dict]:
    store = DBStore()
    data, _ = await store.get_default_data(test_name)
    return data


@api_router.get("/default/result/{test_name}/changes")
async def default_changes(test_name: str):
    return await calc_changes(test_name)


# Must come at the end, once we've setup all the routes
app.include_router(api_router, prefix="/api/v0")
app.include_router(auth.auth_router, prefix="/api/v0")
app.include_router(challenge_publish.cph_router, prefix="/api/v0")
app.include_router(user_router, prefix="/api/v0")
app.include_router(admin_router, prefix="/api/v0")
app.include_router(config_router, prefix="/api/v0")
app.include_router(public_router, prefix="/api/v0")
app.include_router(org_router, prefix="/api/v0")
app.include_router(billing_router, prefix="/api/v0")
app.include_router(pr_router, prefix="/api/v0")
app.include_router(market_router, prefix="/api/v0")


@app.on_event("startup")
async def do_db():
    from backend.db.db import do_on_startup

    await do_on_startup()


def _since_days(days):
    if days is None:
        return None

    return datetime.now(tz=timezone.utc) - timedelta(days=days)


async def get_notifiers(
    notify: Union[int, None],
    config: dict,
    user: User,
    base_url: str = "https://nyrkio.com/result/",
    public_base_url: str = None,
    public_tests: list = None,
    org: dict = None,
) -> list:
    notifiers = []
    exceptions = []

    if notify:
        slack = config.get("slack", {})
        since_days = config.get("since_days", 14)
        since = _since_days(since_days)
        print(f"slack {slack} for user {user.id} since {since_days} days = {since}")
        # TODO: I'll leave the slack config to be attached to the user for now, because someone
        # is already using this. Later we can allow also slack to be configured in the org
        if slack and slack.get("channel"):
            if not user.slack:
                exceptions.append(
                    HTTPException(
                        status_code=400,
                        detail="Slack alerts were requested but Slack integration is not configured for this user ({})".format(
                            user.model_dump()
                        ),
                    )
                )

            url = user.slack["incoming_webhook"]["url"]
            channel = slack["channel"]
            print(f"Appending slack notifier for {url} and {channel}")
            notifiers.append(
                SlackNotifier(
                    url, [channel], since, base_url, public_base_url, public_tests
                )
            )
        gh_id = None
        # If org was passed, this is coming from api/organization.py
        if org is not None:
            gh_id = org["id"]
        else:
            if user.oauth_accounts:
                for account in user.oauth_accounts:
                    if account.oauth_name != "github" or not account.account_id:
                        continue
                    gh_id = account.account_id

        print(f"github {gh_id} for user {user.id}")
        if gh_id is not None:
            db = DBStore()
            gh_config = await db.get_github_installation(gh_id)
            print(gh_config)
            if gh_config:
                print(f"Appending github issue notifier {gh_id} for {user.id}")
                api_url = "https://api.github.com/repos/{}/{}/issues"
                notifiers.append(
                    GitHubIssueNotifier(
                        api_url,
                        gh_config,
                        since,
                        base_url,
                        public_base_url,
                        public_tests,
                    )
                )

    if len(exceptions) > 0:
        if len(exceptions) > 1:
            print(
                "Multiple errors when trying to notify about recent regressions. Only the first one was returned over HTTP to the client:"
            )
        for exc in exceptions:
            print(exc)
        raise exceptions[0]

    return notifiers
