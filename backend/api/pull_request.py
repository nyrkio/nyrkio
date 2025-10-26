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

from typing import Union, Any, Tuple, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi_users import models, BaseUserManager

from backend.api.model import TestResults
from backend.auth import auth
from backend.auth.common import get_user_manager
from backend.api.changes import calc_changes
from backend.db.db import DBStoreResultExists, User, DBStore
from backend.notifiers.github import GitHubCommentNotifier

pr_router = APIRouter(prefix="/pulls")


@pr_router.get("/{repo:path}/{pull_number}/changes/{git_commit}/test/{test_name:path}")
async def get_pr_changes_test_name(
    test_name: str,
    pull_number: int,
    git_commit: str,
    repo: str,
    notify: Union[int, None] = None,
    user: User = Depends(auth.current_active_user),
):
    _ = test_name
    return await _get_pr_changes(
        pull_number, git_commit, repo, test_name, notify, user.id
    )


@pr_router.get("/{repo:path}/{pull_number}/changes/{git_commit}")
async def get_pr_changes(
    pull_number: int,
    git_commit: str,
    repo: str,
    notify: Union[int, None] = None,
    user: User = Depends(auth.current_active_user),
):
    return await _get_pr_changes(pull_number, git_commit, repo, None, notify, user.id)


async def _get_pr_changes(
    pull_number: int,
    git_commit: str,
    repo: str,
    test_name: str,
    notify: Union[int, None] = None,
    user_or_org_id: Any = None,
    repo_owner_id: Any = None,
):
    print(repo_owner_id, user_or_org_id, test_name)
    test_names = None if test_name is None else [test_name]
    store = DBStore()
    if test_names is None:
        # Find out all my test names
        pulls = await store.get_pull_requests_from_the_source(
            user_id=user_or_org_id,
            repo=repo,
            git_commit=git_commit,
            pull_number=pull_number,
            test_names=test_names,
        )
        # print(pulls)
        if not pulls:
            print("got nothing...")
            raise HTTPException(status_code=404, detail="No test results found")
        test_names = []
        for p in pulls:
            test_names.extend(p["test_names"])

    changes = []
    all_results = []
    varying_user_id = repo_owner_id if repo_owner_id else user_or_org_id
    for test_name in test_names:
        # results, _ = await store.get_results(
        #     user_or_org_id, test_name, pull_number, git_commit
        # )
        # pull = await store.get_pull_requests_from_the_source(
        #     user_id=user_or_org_id,
        #     test_names=[test_name],
        #     pull_number=pull_number,
        #     git_commit=git_commit,
        # )
        pull, _ = await store.get_results(
            varying_user_id, test_name, pull_number, git_commit
        )
        # results, _ = await store.get_results(varying_user_id, test_name)
        # print()
        # import pprint
        # pprint.pprint(pull)
        # print()
        # if pull:
        #     results.extend(pull)
        # print(results)
        # print()
        results = pull
        # assert False
        if not len(results) >= 1:
            raise HTTPException(
                status_code=404,
                detail="Did not find any commits for test_name '{}'. Not even {} which is the commit of this pull request.".format(
                    test_names, git_commit
                ),
            )

        all_results.append({test_name: results})
        ch = await calc_changes(
            test_name, varying_user_id, pull_request=pull_number, pr_commit=git_commit
        )
        if ch:
            changes.append(ch)

    public_test_objects, _ = await store.get_public_results(varying_user_id)
    # public_test_names = [t["test_name"] for t in public_test_objects]
    # print(public_test_names)

    if notify and user_or_org_id:
        # TODO(mfleming) in the future we should also support slack
        # slack = config.get("slack", {})
        user_config, _ = await store.get_user_config(user_or_org_id)
        notifiers = user_config.get("notifiers", {})
        if notifiers and notifiers.get("github", {}):
            notifier = GitHubCommentNotifier(
                repo, pull_number, "https://nyrkio.com/public/", []
            )
            await notifier.notify(all_results, git_commit, changes)

    return changes


@pr_router.post("/{repo:path}/{pull_number}/result/{test_name:path}")
async def add_pr_result(
    test_name: str,
    test_result: TestResults,
    repo: str,
    pull_number: int,
    token_tup: Tuple[Optional[models.UP], Optional[str]] = Depends(
        auth.current_user_token
    ),
    user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
    # user: User = Depends(auth.current_active_user),
):
    from backend.api.public import _validate_cph_user, _validate_normal_user

    user = await _validate_normal_user(token_tup, user_manager)
    if user.is_cph_user:
        _validate_cph_user(token_tup, repo)

    return await _add_pr_result(test_name, test_result, repo, pull_number, user.id)


@pr_router.put("/{repo:path}/{pull_number}/result/{test_name:path}")
async def put_pr_result(
    test_name: str,
    test_result: TestResults,
    repo: str,
    pull_number: int,
    user: User = Depends(auth.current_active_user),
):
    return await _add_pr_result(
        test_name, test_result, repo, pull_number, user.id, update=True
    )


async def _add_pr_result(
    test_name: str,
    test_result: TestResults,
    repo: str,
    pull_number: int,
    user_or_org_id: Any = None,
    update: bool = False,
):
    results = test_result.root

    store = DBStore()
    try:
        await store.add_results(
            user_or_org_id, test_name, results, pull_number=pull_number, update=update
        )
    except DBStoreResultExists:
        raise HTTPException(
            status_code=400, detail="Result for this pull request already exists"
        )

    # mfleming: The expectation is that this is usually a singleton list.
    for r in results:
        await store.add_pr_test_name(
            user_or_org_id, repo, r.attributes["git_commit"], pull_number, test_name
        )


@pr_router.delete("/{repo:path}/{pull_number}")
async def delete_pr_result(
    repo: str,
    pull_number: int,
    user: User = Depends(auth.current_active_user),
):
    """Delete all results for a pull request."""
    return await _delete_pr_result(repo, pull_number, user.id)


async def _delete_pr_result(
    repo: str,
    pull_number: int,
    user_or_org_id: Any,
):
    store = DBStore()
    pulls = await store.get_pull_requests(user_or_org_id)

    matches = list(
        filter(
            lambda x: x["git_repo"] == repo and x["pull_number"] == pull_number, pulls
        )
    )
    await store.delete_pull_requests(user_or_org_id, repo, pull_number)

    # TODO(mfleming) Again, it'd be better to push this down into the query.
    for match in matches:
        for test_name in match["test_names"]:
            await store.delete_result(
                user_or_org_id, test_name, pull_request=pull_number
            )
    return []


@pr_router.get("/{repo:path}/{pull_number}/result/{git_commit}/test/{test_name:path}")
async def get_pr_commit_result(
    test_name: str,
    repo: str,
    pull_number: int,
    git_commit: str,
    user: User = Depends(auth.current_active_user),
):
    return await _get_pr_result(
        test_name, repo, pull_number, user.id, pr_commit=git_commit
    )


@pr_router.get("/{repo:path}/{pull_number}/result/{test_name:path}")
async def get_pr_result(
    test_name: str,
    repo: str,
    pull_number: int,
    user: User = Depends(auth.current_active_user),
):
    return await _get_pr_result(test_name, repo, pull_number, user.id)


async def _get_pr_result(
    test_name: str,
    repo: str,
    pull_number: int,
    user_or_org_id: Any = None,
    pr_commit: str = None,
):
    store = DBStore()
    results, _ = await store.get_results(
        user_or_org_id, test_name, pull_request=pull_number, pr_commit=pr_commit
    )
    if not len(results) > 0:
        raise HTTPException(status_code=404, detail="Not Found")

    return results


@pr_router.get("")
async def get_pr_results(user: User = Depends(auth.current_active_user)):
    print('just "" after /pulls')
    return await _get_pr_results(user_or_org_id=user.id)


async def _get_pr_results(
    user_or_org_id: Any = None,
    repo: str = None,
    branch: str = None,
    test_names: str = None,
):
    store = DBStore()
    return await store.get_pull_requests_from_the_source(
        user_id=user_or_org_id, repo=repo, branch=branch, test_names=test_names
    )
