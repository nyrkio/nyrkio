"""
This API allows users to upload results from GitHub pull requests.

These results are different from regular results in that they are not stored
with the long-term results for a test series at /api/v0/result. As such, PR
results for a given branch have no influence on change detection for other PRs
or branches. This is necessary because there's no guarantee that the code in a PR
will ever be merged into the main branch.

Unlike the regular results API, the PR API works with test results in batches,
e.g. a single pull request holds multiple test results.

Additionally, the statistical methods used for change detection are different
from the regular results API. Given a historical series of test results, the PR
API will detect performance changes in the most recent result.
"""

import logging
from typing import Union

from fastapi import APIRouter, Depends, HTTPException

from backend.api.model import TestResults
from backend.auth import auth
from backend.api.changes import calc_changes
from backend.core.config import Config
from backend.db.db import DBStoreResultExists, User, DBStore
from backend.notifiers.github import GitHubCommentNotifier

pr_router = APIRouter()


@pr_router.get("/pulls/{pull_number}/changes/{git_commit}")
async def get_pr_changes(
    pull_number: int,
    git_commit: str,
    notify: Union[int, None] = None,
    user: User = Depends(auth.current_active_user),
):
    store = DBStore()
    test_names = await store.get_pr_test_names(user, git_commit, pull_number)
    if not test_names:
        raise HTTPException(status_code=404, detail="No test results found")

    changes = []
    repo = None
    user_config = await store.get_user_config(user)
    all_results = []
    for test_name in test_names:
        disabled = await store.get_disabled_metrics(user, test_name)
        results = await store.get_results(user, test_name, pull_number)
        all_results.append(results)
        if not repo:
            # We don't actually enforce this anywhere but we assume that all
            # results are from the same repository.
            logging.error(f"Results is {results}")
            logging.error(f"Results[0] is {results[0]}")
            values = {r["attributes"]["git_repo"] for r in results}
            if len(values) > 1:
                logging.error(
                    f"Multiple git_repo values in pull test results: {values}"
                )

            repo = values.pop()

        core_config = user_config.get("core", {})
        if core_config:
            core_config = Config(**core_config)
        ch = await calc_changes(test_name, results, disabled, core_config)
        if ch:
            changes.append(ch)

    logging.error(f"Changes is {changes}")
    logging.error(f"Notify is {notify}")
    if notify:
        # TODO(mfleming) in the future we should also support slack
        # slack = config.get("slack", {})
        notifiers = user_config.get("notifiers", {})
        logging.error(f"notifiers is {notifiers}")
        if (
            notifiers
            and notifiers.get("github", {})
            and repo.startswith("https://github.com")
        ):
            # access_token = None
            # for account in user.oauth_accounts:
            #     if account.oauth_name == "github":
            #         access_token = account.access_token

            # if access_token is None:
            #     raise HTTPException(status_code=400, detail="GitHub not configured")

            notifier = GitHubCommentNotifier(repo, pull_number)
            logging.error(f"notifier is {notifier}")
            await notifier.notify(all_results, changes)

    return changes


@pr_router.post("/pulls/{pull_number}/result/{test_name:path}")
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

    # mfleming: The expectation is that this is usually a singleton list.
    for r in results:
        await store.add_pr_test_name(
            user, r.attributes["git_commit"], pull_number, test_name
        )


@pr_router.delete("/pulls/{pull_number}/result/{test_name:path}")
async def delete_pr_result(
    test_name: str,
    timestamp: Union[int, None] = None,
    user: User = Depends(auth.current_active_user),
):
    store = DBStore()
    await store.delete_result(user, test_name, timestamp)
    return []


@pr_router.get("/pulls/{pull_number}/result/{test_name:path}")
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
    logging.error(f"Results is {results}")
    return [{"test_name": name} for name in results]
