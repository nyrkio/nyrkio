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

Individual users own pull requests. It is not possible for an organisation to
own a pull request.

Since pull requests are intrinsically tied to GitHub, the 'repo' parameter below
should not include the protocol or domain name. It should be in the form
'org/repo'.  For one, it's superfluous information (you can only use the pull
request API with GitHub repositories) and secondly, it means users don't have to
worry about url encoding.

All of this is in contrast to the 'git_repo' field in the individual test
results where it is the full git repository URL.

This is true for all the API endpoints in this file.
"""

import logging
from typing import Union

from fastapi import APIRouter, Depends, HTTPException

from backend.api.model import TestResults
from backend.auth import auth
from backend.api.changes import calc_changes
from backend.db.db import DBStoreResultExists, User, DBStore
from backend.notifiers.github import GitHubCommentNotifier

pr_router = APIRouter()


@pr_router.get("/pulls/{repo:path}/{pull_number}/changes/{git_commit}")
async def get_pr_changes(
    pull_number: int,
    git_commit: str,
    repo: str,
    notify: Union[int, None] = None,
    user: User = Depends(auth.current_active_user),
):
    store = DBStore()
    pulls = await store.get_pull_requests(user.id, repo, git_commit, pull_number)
    if not pulls:
        raise HTTPException(status_code=404, detail="No test results found")

    if len(pulls) > 1:
        # This should be impossible. If it happens, it's a bug.
        # It's not catastrophic since we just process the first result.
        logging.error(f"Multiple results for pull request: {pulls}")

    changes = []
    user_config, _ = await store.get_user_config(user.id)

    pr = pulls[0]
    all_results = []
    for test_name in pr["test_names"]:
        results, _ = await store.get_results(
            user.id, test_name, pull_number, git_commit
        )
        if not len(results) >= 1:
            raise HTTPException(
                status_code=404,
                detail="Did not find any commits for test_name '{}'. Not even {} which is the commit of this pull request.".format(
                    test_name, git_commit
                ),
            )

        all_results.append({test_name: results})
        ch = await calc_changes(
            test_name, user.id, pull_request=pull_number, pr_commit=git_commit
        )
        if ch:
            changes.append(ch)

    if notify:
        # TODO(mfleming) in the future we should also support slack
        # slack = config.get("slack", {})
        notifiers = user_config.get("notifiers", {})
        if notifiers and notifiers.get("github", {}):
            notifier = GitHubCommentNotifier(repo, pull_number)
            await notifier.notify(all_results, git_commit, changes)

    return changes


@pr_router.post("/pulls/{repo:path}/{pull_number}/result/{test_name:path}")
async def add_pr_result(
    test_name: str,
    test_result: TestResults,
    repo: str,
    pull_number: int,
    user: User = Depends(auth.current_active_user),
):
    results = test_result.root

    store = DBStore()
    try:
        await store.add_results(user.id, test_name, results, pull_number=pull_number)
    except DBStoreResultExists:
        raise HTTPException(
            status_code=400, detail="Result for this pull request already exists"
        )

    # mfleming: The expectation is that this is usually a singleton list.
    for r in results:
        await store.add_pr_test_name(
            user.id, repo, r.attributes["git_commit"], pull_number, test_name
        )


@pr_router.delete("/pulls/{repo:path}/{pull_number}")
async def delete_pr_result(
    repo: str,
    pull_number: int,
    user: User = Depends(auth.current_active_user),
):
    """Delete all results for a pull request."""
    store = DBStore()
    pulls = await store.get_pull_requests(user.id)

    matches = list(
        filter(
            lambda x: x["git_repo"] == repo and x["pull_number"] == pull_number, pulls
        )
    )
    await store.delete_pull_requests(user.id, repo, pull_number)

    # TODO(mfleming) Again, it'd be better to push this down into the query.
    for match in matches:
        for test_name in match["test_names"]:
            await store.delete_result(user.id, test_name, pull_request=pull_number)
    return []


@pr_router.get("/pulls/{repo:path}/{pull_number}/result/{test_name:path}")
async def get_pr_result(
    test_name: str,
    repo: str,
    pull_number: int,
    user: User = Depends(auth.current_active_user),
):
    store = DBStore()
    pulls = await store.get_pull_requests(user.id)

    a = list(
        filter(
            lambda x: x["git_repo"] == repo and x["pull_number"] == pull_number, pulls
        )
    )
    if not list(filter(lambda x: test_name in x["test_names"], a)):
        raise HTTPException(status_code=404, detail="Not Found")

    results, _ = await store.get_results(user.id, test_name, pull_request=pull_number)

    # Filter out the results that are not from the repo
    # TODO(mfleming): We should push this down into the query to the db.
    results = [
        r
        for r in results
        if r["attributes"]["git_repo"] == "https://github.com/" + repo
    ]
    return results


@pr_router.get("/pulls")
async def get_pr_results(user: User = Depends(auth.current_active_user)):
    store = DBStore()
    return await store.get_pull_requests(user.id)
