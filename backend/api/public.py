from typing import Dict, List
from fastapi import APIRouter, HTTPException

from backend.auth import auth
from backend.core.config import Config
from backend.db.db import DBStore

"""
Test results can be made publicly available to everyone so that users can
view them without creating an account or logging in.

The url scheme for public results is,

  https://nyrk.io/public/github-org/github-repo/branch/testname

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
    return await store.get_public_results()


def extract_git_repo(test_name: str) -> Dict:
    parts = test_name.split("/")
    if len(parts) < 2:
        raise ValueError(f"Invalid test name: {test_name}")

    org = parts[0]
    repo = parts[1]

    # TODO(mfleming) We assume that the protocol is https which may not
    # be true, e.g. for private repositories.
    return f"https://github.com/{org}/{repo}"


def get_short_test_name(test_name: str) -> str:
    # Skip the first three parts of the test name
    parts = test_name.split("/")
    if len(parts) < 4:
        raise HTTPException(status_code=404, detail="No such test exists")

    # org/repo/branch/testname
    short_test_name = "/".join(parts[3:])
    if not short_test_name:
        raise HTTPException(status_code=404, detail="No such test exists")
    return short_test_name


@public_router.get("/result/{test_name:path}/changes")
async def changes(test_name: str):
    store = DBStore()
    user_id = await store.get_public_user(test_name)
    if not user_id:
        raise HTTPException(status_code=404, detail="No such test exists")

    short_test_name = get_short_test_name(test_name)
    user = await auth.get_user(user_id)
    results = await store.get_results(user, short_test_name)
    disabled = await store.get_disabled_metrics(user, short_test_name)

    config = await store.get_user_config(user)
    core_config = config.get("core", None)
    if core_config:
        core_config = Config(**core_config)

    from backend.api.api import calc_changes

    return await calc_changes(short_test_name, results, disabled, core_config, [])


@public_router.get("/result/{test_name:path}")
async def get_result(test_name: str) -> List[Dict]:
    short_test_name = get_short_test_name(test_name)
    store = DBStore()
    user_id = await store.get_public_user(test_name)
    if not user_id:
        raise HTTPException(status_code=404, detail="No such test exists")

    user = await auth.get_user(user_id)
    return await store.get_results(user, short_test_name)
