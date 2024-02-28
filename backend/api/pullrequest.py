"""
This API allows users to upload results from GitHub pull requests.

These results are different from regular results in that they are not stored
with the long-term results for a test series at /api/v0/result. As such, PR
results for a given branch have no influence on change detection for other PRs
or branches. This is necessary because there's no guarantee that the code in a PR
will ever be merged into the main branch.
"""

from typing import Union

from fastapi import APIRouter, Depends, HTTPException

from backend.api.model import TestResults
from backend.auth import auth
from backend.core.config import Config
from backend.db.db import DBStoreResultExists, User, DBStore

pr_router = APIRouter()


@pr_router.get("/pulls/{test_name:path}/{pull_number}/changes")
async def get_pr_changes(
    test_name: str, pull_number: int, user: User = Depends(auth.current_active_user)
):
    store = DBStore()
    results = await store.get_results(user, test_name, pull_number)
    disabled = await store.get_disabled_metrics(user, test_name)

    config = await store.get_user_config(user)
    config = config.get("core", None)
    if config:
        config = Config(**config)

    from backend.api.api import calc_changes

    return await calc_changes(test_name, results, disabled, config)


@pr_router.post("/pulls/{test_name:path}/{pull_number}")
async def add_pr_result(
    test_name: str,
    test_result: TestResults,
    pull_number: int,
    user: User = Depends(auth.current_active_user),
):
    results = test_result.root

    store = DBStore()
    try:
        await store.add_results(user, test_name, results, pull_number)
    except DBStoreResultExists:
        raise HTTPException(
            status_code=400, detail="Result for this pull request already exists"
        )


@pr_router.delete("/pulls/{test_name:path}/{pull_number}")
async def delete_pr_result(
    test_name: str,
    timestamp: Union[int, None] = None,
    user: User = Depends(auth.current_active_user),
):
    store = DBStore()
    await store.delete_result(user, test_name, timestamp)
    return []


@pr_router.get("/pulls/{test_name:path}/{pull_number}")
async def get_pr_result(test_name: str, user: User = Depends(auth.current_active_user)):
    store = DBStore()
    test_names = await store.get_test_names(user)

    if not list(filter(lambda name: name == test_name, test_names)):
        raise HTTPException(status_code=404, detail="Not Found")

    results = await store.get_results(user, test_name)
    return results


@pr_router.get("/pulls")
async def get_pr_results(user: User = Depends(auth.current_active_user)):
    store = DBStore()
    results = await store.get_test_names(user)
    return [{"test_name": name} for name in results]
