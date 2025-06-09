from typing import Dict, List
from fastapi import APIRouter, HTTPException

from backend.db.db import DBStore
from backend.db.list_changes import change_points_per_commit
from backend.api.pull_request import _get_pr_results, _get_pr_result

"""
Test results can be made publicly available to everyone so that users can
view them without creating an account or logging in.

The url scheme for public results is,

  https://nyrkio.com/public/github-org/github-repo/branch/testname

Internally, Nyrkiö maintains a mapping between user test results and
public results. Since there's no user namespace in the above url scheme,
only *ONE* user test can be mapped to a given public url.

Below is the code for a corresponding public API in the backend and this API
is read-only. Modifications can still be made by the user via the regular
API at /api/v0/result/.

In other words, for public test results there are two entry points to the
same data series:

  1. public (read-only for everyone), via /api/v0/public and the above urls
  2. private (read-write for owning authenticated user) via /api/v0/result/
"""


async def _figure_out_user_and_test(public_test_name, prefix=False):
    test_name = public_test_name
    store = DBStore()
    test_entry = False
    all_matching = []
    if prefix:
        all_matching = await lookup_public_test_prefix(store, test_name)
        if all_matching:
            test_entry = all_matching[0]
    else:
        test_entry = await lookup_public_test(store, test_name)
    if not test_entry:
        raise HTTPException(status_code=404, detail="No such test exists")

    user_id = test_entry["user_id"]
    if is_user_id(user_id):
        test_name = test_entry["test_name"]

    if prefix:
        return user_id, all_matching

    return user_id, test_name


public_router = APIRouter(prefix="/public")


@public_router.get("/results")
async def results() -> List[Dict]:
    store = DBStore()
    data, meta = await store.get_public_results()
    if not data:
        return []
    return [{"test_name": build_public_test_name(r)} for r in data]


@public_router.get("/changes/perCommit/{test_name_prefix:path}")
async def changes_per_commit(test_name_prefix: str, commit: str = None):
    test_name_prefix = test_name_prefix.replace("https://github.com/", "")
    test_name_prefix = test_name_prefix.replace("https:/github.com/", "")
    user_or_org_id, all_matching = await _figure_out_user_and_test(
        test_name_prefix, prefix=True
    )
    all_changes = []
    for r in all_matching:
        all_changes += await change_points_per_commit(
            user_or_org_id, r["test_name"], commit
        )
    return all_changes


@public_router.get("/result/{test_name:path}/changes")
async def changes(test_name: str):
    user_or_org_id, test_name = await _figure_out_user_and_test(test_name)
    from backend.api.api import calc_changes

    return await calc_changes(test_name, user_or_org_id)


@public_router.get("/result/summarySiblings")
async def get_subtree_summary_siblings_root() -> Dict:
    """
    TODO: Could return an aggregation of every public subtree by fetching all and smashing together?
    """
    return {}


@public_router.get("/result/{parent_test_name_prefix:path}/summarySiblings")
async def get_subtree_summary_siblings(parent_test_name_prefix: str) -> Dict:
    """
    Like /summary but client will ask for the parent prefix, and we return all children of that parent.
    This allows a single call to replace separate HTTP calls for each list entry.
    """
    user_or_org_id = None
    int_parent_name = None
    public_test_prefix = None
    store = DBStore()
    public_results, _ = await store.get_public_results()

    for test_result in public_results:
        int_parent_name = internal_test_name(
            test_result["user_id"], parent_test_name_prefix
        )
        if test_result["test_name"].startswith(int_parent_name):
            user_or_org_id = test_result["user_id"]
            public_test_prefix = extract_public_test_name(test_result["attributes"])
            break

    if not user_or_org_id:
        raise HTTPException(status_code=404, detail="No such test exists")

    cache = await store.get_summaries_cache(user_or_org_id)
    # This is a public API but we're holding the names of all the non-public tests and change points
    # this user_or_org_id. We want to return just the one where user is now.
    filtered_cache = {}
    for k, v in cache.items():
        if k.startswith(int_parent_name):
            filtered_cache["/" + public_test_prefix + "/" + k] = v
    return filtered_cache


@public_router.get("/result/{test_name:path}")
async def get_result(test_name: str) -> List[Dict]:
    store = DBStore()
    test_entry = await lookup_public_test(store, test_name)
    if not test_entry:
        raise HTTPException(status_code=404, detail="No such test exists")

    id = test_entry["user_id"]
    if is_user_id(id):
        test_name = test_entry["test_name"]

    data, _ = await store.get_results(id, test_name)
    return data


@public_router.get(
    "/pulls/{repo:path}/{pull_number}/result/{git_commit}/test/{test_name:path}"
)
async def get_pr_commit_result(
    test_name: str,
    repo: str,
    pull_number: int,
    git_commit: str,
):
    user_or_org_id, repo, branch, test_name = get_public_namespace_parts(test_name)
    return await _get_pr_result(
        test_name, repo, pull_number, user_or_org_id, pr_commit=git_commit
    )


@public_router.get("/pulls/{test_name_public_prefix:path}")
async def get_pr_results(test_name_public_prefix: str):
    if len(test_name_public_prefix) == 0:
        raise HTTPException(
            status_code=404,
            detail="For /public/result/pulls/* you must append at least the username or org name component of the path´",
        )

    user_or_org_id, repo, branch, test_name = get_public_namespace_parts(
        test_name_public_prefix
    )
    test_name_list = [test_name] if test_name else []
    return await _get_pr_results(
        user_or_org_id, repo=repo, branch=branch, test_names=test_name_list
    )


# TODO(Henrik): Add a query to `store` where we use test_name in the query, not here
async def lookup_public_test(store, test_name):
    results, _ = await store.get_public_results()
    for r in results:
        if build_public_test_name(r) == test_name:
            return r
    return None


async def lookup_public_test_prefix(store, test_name):
    results, _ = await store.get_public_results()
    all_matching = []
    for r in results:
        public_test = build_public_test_name(r)
        if public_test.startswith(test_name):
            all_matching.append(r)
    return all_matching


def extract_public_test_name(attributes):
    # TODO(mfleming) we assume a https://github.com repo
    name = attributes["git_repo"].replace("https://github.com/", "")
    name += "/" + attributes["branch"]
    return name


def is_user_id(id):
    return not isinstance(id, int)


def build_public_test_name(test_entry):
    """
    The way that we map public test names to individual test results is
    different depending on whether the owner of the public test is an
    individual user or a GitHub organization.

    This is for historic reasons -- the individual user API was implemented
    first and doesn't require using a GH org/repo as part of the test name,
    which means we need to build it to make public test names unique.
    """
    if is_user_id(test_entry["user_id"]):
        return (
            extract_public_test_name(test_entry["attributes"])
            + "/"
            + test_entry["test_name"]
        )

    return test_entry["test_name"]


def internal_test_name(user_id, public_test_name):
    name = None
    if is_user_id(user_id):
        name = public_test_name.replace("https://github.com/", "")
        name = name.replace("https:/github.com/", "")
        parts = name.split("/")
        if len(parts) >= 3:
            # org = parts[0]
            # repo = parts[1]
            # branch = parts[2]
            return "/".join(parts[3:])

    return name


def get_public_namespace_parts(public_test_name):
    public_test_name = public_test_name.replace("https://github.com/", "")
    public_test_name = public_test_name.replace("https:/github.com/", "")

    parts = public_test_name.split("/")
    org = parts.pop(0) if parts else None
    repo = parts.pop(0) if parts else None
    branch = parts.pop(0) if parts else None
    test_name = "/".join(parts) if parts else None
    return org, repo, branch, test_name
