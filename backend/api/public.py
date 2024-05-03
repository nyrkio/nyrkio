from typing import Dict, List
from fastapi import APIRouter, HTTPException

from backend.db.db import DBStore

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

public_router = APIRouter(prefix="/public")


@public_router.get("/results")
async def results() -> List[Dict]:
    store = DBStore()
    data, meta = await store.get_public_results()
    if not data:
        return []
    return [{"test_name": build_public_test_name(r)} for r in data]


@public_router.get("/result/{test_name:path}/changes")
async def changes(test_name: str):
    store = DBStore()
    test_entry = await lookup_public_test(store, test_name)
    if not test_entry:
        raise HTTPException(status_code=404, detail="No such test exists")

    user_id = test_entry["user_id"]
    if is_user_id(user_id):
        test_name = test_entry["test_name"]

    config, _ = await store.get_user_config(user_id)

    from backend.api.api import calc_changes

    return await calc_changes(test_name, user_id)


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


# TODO(Henrik): Add a query to `store` where we use test_name in the query, not here
async def lookup_public_test(store, test_name):
    results, _ = await store.get_public_results()
    print(results)
    for r in results:
        if build_public_test_name(r) == test_name:
            return r
    return None


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
