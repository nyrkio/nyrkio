from typing import Dict, List, Union
from fastapi import APIRouter, Depends, HTTPException

from backend.api.config import TestConfigList
from backend.api.model import TestResults
from backend.api.public import build_public_test_name
from backend.api.user import UserConfig, validate_config
from backend.auth import auth
from backend.core.config import Config
from backend.db.db import DBStore, User

"""
Per-organization test result API endpoints.

These endpoints allow GitHub users that belong to the same organization to
share test results.
"""

org_router = APIRouter(prefix="/orgs")


def get_user_orgs(user: User) -> List[Dict]:
    if not user.oauth_accounts:
        return []

    orgs = []
    for account in user.oauth_accounts:
        if account.oauth_name != "github" or not account.organizations:
            continue

        for org in account.organizations:
            orgs.append(org)
    return orgs


def get_org_with_raise(orgs, org_string):
    """
    Lookup the organization with the given name in the list of organizations.

    If the organization is not found, raise an HTTPException.
    """
    for o in orgs:
        print(o)
        if "login" in o and o["login"] == org_string:
            return o
        if "organization" in o and o["organization"].get("login", None) == org_string:
            return o["organization"]
    raise HTTPException(status_code=404, detail="No such organization exists")


@org_router.get("/result/{test_name:path}/changes")
async def changes(test_name: str, user: User = Depends(auth.current_active_user)):
    user_orgs = get_user_orgs(user)
    org = get_org_with_raise(user_orgs, test_name.split("/")[0])

    store = DBStore()
    test_names = await store.get_test_names(org["id"])
    if not list(filter(lambda name: name == test_name, test_names)):
        raise HTTPException(status_code=404, detail="Not Found")

    config, _ = await store.get_user_config(org["id"])
    core_config = config.get("core", None)
    if core_config:
        core_config = Config(**core_config)

    from backend.api.api import calc_changes

    return await calc_changes(test_name, org["id"])


@org_router.get("/result/{test_name:path}")
async def results(
    test_name: str,
    user: User = Depends(auth.current_active_user),
) -> Union[List[Dict], List]:
    user_orgs = get_user_orgs(user)
    org = get_org_with_raise(user_orgs, test_name.split("/")[0])
    store = DBStore()

    test_names = await store.get_test_names(org["id"])
    if not list(filter(lambda name: name == test_name, test_names)):
        raise HTTPException(status_code=404, detail="Not Found")

    results, _ = await store.get_results(org["id"], test_name)
    return results if results else []


@org_router.post("/result/{test_name:path}")
async def add_result(
    test_name: str, data: TestResults, user: User = Depends(auth.current_active_user)
):
    user_orgs = get_user_orgs(user)
    org = get_org_with_raise(user_orgs, test_name.split("/")[0])
    org_id = org["id"]

    store = DBStore()
    await store.add_results(org_id, test_name, data.root)
    return []


@org_router.delete("/result/{test_name:path}")
async def delete_result(
    test_name: str,
    timestamp: Union[int, None] = None,
    user: User = Depends(auth.current_active_user),
):
    user_orgs = get_user_orgs(user)
    org = get_org_with_raise(user_orgs, test_name.split("/")[0])

    store = DBStore()
    test_names = await store.get_test_names(org["id"])
    if not list(filter(lambda name: name == test_name, test_names)):
        raise HTTPException(status_code=404, detail="Not Found")

    await store.delete_result(org["id"], test_name, timestamp)
    return []


@org_router.get("/")
async def get_orgs(user: User = Depends(auth.current_active_user)) -> List[Dict]:
    """
    Return the list of organizations that the user belongs to.
    """
    return get_user_orgs(user)


@org_router.get("/results")
async def get_results(
    user: User = Depends(auth.current_active_user),
) -> List[Dict]:
    """
    Return the list of test results for all organizations that the user belongs to.
    """
    store = DBStore()
    results = []
    for org in get_user_orgs(user):
        print(org)
        if "id" in org:
            org_id = org["id"]
            res = await store.get_test_names(org_id)
            if res:
                results.extend(res)

    return [{"test_name": name} for name in results]


#
# Per-organization test configuration API endpoints
#
@org_router.post("/config/{test_name:path}")
async def set_config(
    test_name: str, data: TestConfigList, user: User = Depends(auth.current_active_user)
) -> Dict:
    user_orgs = get_user_orgs(user)
    org = get_org_with_raise(user_orgs, test_name.split("/")[0])
    org_id = org["id"]

    store = DBStore()
    test_names = await store.get_test_names(org_id)
    if not list(filter(lambda name: name == test_name, test_names)):
        raise HTTPException(status_code=404, detail="Test name not found")

    # Even though we accept a list of test configurations, for the organization
    # endpoint it only makes sense to accept a single configuration since the url
    # tells us the one and only test name. This is unlike the /config endpoint
    # where we can have multiple test configurations.
    #
    # This way we can share client code between the two endpoints.

    if len(data.root) != 1:
        raise HTTPException(
            status_code=400, detail="Too many test configurations, expected 1"
        )

    configs = [elem.model_dump() for elem in data.root]

    conf = dict(configs[0])
    conf["user_id"] = org_id
    conf["test_name"] = test_name
    name = build_public_test_name(conf)

    public_tests, meta = await store.get_public_results()
    public_test_names = [build_public_test_name(p) for p in public_tests]

    if conf["public"] and name in public_test_names:
        raise HTTPException(
            status_code=409, detail=f"Public test already exists for {name}"
        )

    await store.set_test_config(org_id, test_name, configs)
    return {}


@org_router.get("/config/{test_name:path}")
async def get_config(
    test_name: str, user: User = Depends(auth.current_active_user)
) -> List[Dict]:
    user_orgs = get_user_orgs(user)
    org = get_org_with_raise(user_orgs, test_name.split("/")[0])
    org_id = org["id"]

    store = DBStore()
    test_names = await store.get_test_names(org_id)
    if not list(filter(lambda name: name == test_name, test_names)):
        raise HTTPException(status_code=404, detail="Not Found")

    config, _ = await store.get_test_config(org_id, test_name)
    return config


@org_router.delete("/config/{test_name:path}")
async def delete_config(
    test_name: str, user: User = Depends(auth.current_active_user)
) -> Dict:
    user_orgs = get_user_orgs(user)
    org = get_org_with_raise(user_orgs, test_name.split("/")[0])
    org_id = org["id"]

    store = DBStore()
    test_names = await store.get_test_names(org_id)
    if not list(filter(lambda name: name == test_name, test_names)):
        raise HTTPException(status_code=404, detail="Not Found")

    await store.delete_test_config(org_id, test_name)
    return {}


#
# Per-organization configuration endpoints
#
@org_router.get("/org/{org_name:path}")
async def get_org_config(
    org_name: str, user: User = Depends(auth.current_active_user)
) -> Dict:
    user_orgs = get_user_orgs(user)
    org = get_org_with_raise(user_orgs, org_name)

    store = DBStore()
    config, _ = await store.get_user_config(org["id"])
    return config


@org_router.post("/org/{org_name:path}")
async def set_org_config(
    org_name: str, data: UserConfig, user: User = Depends(auth.current_active_user)
) -> Dict:
    user_orgs = get_user_orgs(user)
    org = get_org_with_raise(user_orgs, org_name)

    validate_config(data)

    store = DBStore()
    await store.set_user_config(org["id"], data.model_dump())
    return {}
