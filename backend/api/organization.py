import logging
from typing import Dict, List, Union, Annotated, Form
from fastapi import APIRouter, Depends, HTTPException

from backend.api.config import TestConfigList
from backend.api.model import TestResults
from backend.api.public import build_public_test_name
from backend.api.user import UserConfig, validate_config
from backend.auth import auth
from backend.core.config import Config
from backend.db.db import DBStore, User
from backend.api.pull_request import (
    _get_pr_results,
    _get_pr_result,
    _delete_pr_result,
    _add_pr_result,
    _get_pr_changes,
)
from backend.db.list_changes import change_points_per_commit

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
        # print(o)
        if "login" in o and o["login"] == org_string:
            return o
        if "organization" in o and o["organization"].get("login", None) == org_string:
            return o["organization"]
    raise HTTPException(status_code=404, detail="No such organization exists")


@org_router.get("/changes/perCommit/{test_name_prefix:path}")
async def changes_per_commit(
    test_name_prefix: str,
    commit: str = None,
    user: User = Depends(auth.current_active_user),
):
    user_orgs = get_user_orgs(user)
    org = get_org_with_raise(user_orgs, test_name_prefix.split("/")[0])
    return await change_points_per_commit(org["id"], test_name_prefix, commit)


@org_router.get("/result/{test_name:path}/changes")
async def changes(
    test_name: str,
    notify: Union[int, None] = None,
    user: User = Depends(auth.current_active_user),
):
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

    from backend.api.api import calc_changes, get_notifiers

    public_base_url = None
    public_test_objects, public_test_objects_meta = await store.get_public_results(
        org["id"]
    )
    if public_test_objects:
        # When an org owns a test, it already has the org name as prefix
        public_base_url = "https://nyrkio.com/public/"
    public_test_names = [entry["test_name"] for entry in public_test_objects]

    notifiers = await get_notifiers(
        notify,
        config,
        user,
        base_url="https://nyrkio.com/orgs/",
        public_base_url=public_base_url,
        public_tests=public_test_names,
        org=org,
    )
    return await calc_changes(test_name, org["id"], notifiers)


@org_router.get("/result/{test_name_prefix:path}/summary")
async def get_subtree_summary(
    test_name_prefix: str, user: User = Depends(auth.current_active_user)
) -> Dict:
    user_orgs = get_user_orgs(user)
    org = get_org_with_raise(user_orgs, test_name_prefix.split("/")[0])
    store = DBStore()
    cache = await store.get_summaries_cache(org["id"])
    if test_name_prefix in cache:
        return cache[test_name_prefix]

    raise HTTPException(status_code=404, detail="Not Found")


@org_router.get("/result/summarySiblings")
async def get_subtree_summary_siblings_root(
    user: User = Depends(auth.current_active_user),
) -> Dict:
    """
    For orgs this isn't possible because each org has a different org id
    """
    return {}


@org_router.get("/result/{parent_test_name_prefix:path}/summarySiblings")
async def get_subtree_summary_siblings(
    parent_test_name_prefix: str, user: User = Depends(auth.current_active_user)
) -> Dict:
    """
    Like /summary but client will ask for the parent prefix, and we return all children of that parent.
    This allows a single call to replace separate HTTP calls for each list entry.
    """
    user_orgs = get_user_orgs(user)
    org = get_org_with_raise(user_orgs, parent_test_name_prefix.split("/")[0])
    store = DBStore()
    cache = await store.get_summaries_cache(org["id"])

    children = {}
    length = len(parent_test_name_prefix)
    for k, v in cache.items():
        if len(k) >= length and k[:length] == parent_test_name_prefix:
            children[k] = v

    if children:
        return children

    raise HTTPException(status_code=404, detail="Not Found")


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
    return await changes(test_name, notify=1, user=user)


@org_router.put("/result/{test_name:path}")
async def update_result(
    test_name: str, data: TestResults, user: User = Depends(auth.current_active_user)
):
    user_orgs = get_user_orgs(user)
    org = get_org_with_raise(user_orgs, test_name.split("/")[0])
    org_id = org["id"]

    store = DBStore()
    await store.add_results(org_id, test_name, data.root, update=True)
    return await changes(test_name, notify=1, user=user)


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
        if "organization" in org:
            org_id = org["organization"]["id"]
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
    # Need some more generic solution to this but...
    # Translate MongoDB ObjectId before this goes to JSON
    if (
        config.get("billing") is not None
        and config.get("billing", {}).get("paid_by") is not None
    ):
        config["billing"]["paid_by"] = str(config.get("billing", {}).get("paid_by"))
    if (
        config.get("billing_runners") is not None
        and config.get("billing_runners", {}).get("paid_by") is not None
    ):
        config["billing_runners"]["paid_by"] = str(
            config.get("billing_runners", {}).get("paid_by")
        )
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


planmap = {
    "simple_business_monthly": "sub",
    "simple_business_yearly": "sub",
    "simple_enterprise_monthly": "sub",
    "simple_enterprise_yearly": "sub",
    "simple_business_monthly_251": "sub",
    "simple_business_yearly_2409": "sub",
    "simple_enterprise_monthly_627": "sub",
    "simple_enterprise_yearly_6275": "sub",
    "simple_test_monthly": "test",
    "simple_test_yearly": "test",
    "runner_postpaid_10": "post",
    "runner_postpaid_13": "post",
    "runner_prepaid_10": "pre",
}


@org_router.get("/subscriptions")
async def get_org_subscriptions(
    plan: str,
    user: User = Depends(auth.current_active_user),
) -> List[Dict]:
    store = DBStore()
    return_list = []
    user_orgs = get_user_orgs(user)
    # This could have been a join...
    for org in user_orgs:
        logging.info(org)
        paid_by = None
        config, _ = await store.get_user_config(org["organization"]["id"])
        billing_key = "billing"
        if planmap[plan] == "post":
            billing_key = "billing_runners"

        paid_by = config.get(billing_key, {}).get("paid_by")
        if paid_by == user.id:
            paid_by = True
        elif paid_by is None or (not paid_by):
            paid_by = False
        else:
            # Not empty and not me, so paid by someone else
            someone = store.get_user_without_any_fastapi_nonsense(paid_by)
            if "email" in someone:
                paid_by = someone["email"]
            elif "github_username" in someone:
                paid_by = someone["github_username"]

        return_obj = {
            "name": org.get("organization", {}).get("login", "Org name is missing?"),
            "paid_by": paid_by,
        }
        logging.info(return_obj)
        return_list.append(return_obj)

    return return_list


@org_router.post("/subscriptions/pay_for")
async def pay_for(
    plan: Annotated[str, Form()],
    orgs: Annotated[List[Dict], Form()],
    user: User = Depends(auth.current_active_user),
) -> Dict:
    db = DBStore()

    plan2 = planmap[plan]
    billing_key = "billing"
    if plan2 == "post":
        billing_key = "billing_runners"

    incoming_orgs = {(o.name, o.paid_by_me) for o in orgs}
    user_orgs = get_user_orgs(user)
    for o in user_orgs:
        if o["login"] in incoming_orgs.keys():
            config, _ = db.get_user_config(o["id"])
            if (
                billing_key in config
                and "paid_by" in config[billing_key]
                and config[billing_key]["paid_by"] != user.id
            ):
                raise HTTPException(
                    status_code=401,
                    detail=f"You cannot set 'paid_by' for {o['login']} because it is already pid by someone else.",
                )

    for o in user_orgs:
        if o["login"] in incoming_orgs.keys():
            paid_by = None
            if isinstance(incoming_orgs[o["login"]], bool):
                if incoming_orgs[o["login"]]:
                    paid_by = user.id
                if not incoming_orgs[o["login"]]:
                    paid_by = None

                db.set_user_config(
                    o["id"],
                    {
                        billing_key: {
                            "paid_by": paid_by,
                            "plan": plan,
                            "customer_id": None,
                            "session_id": None,
                        }
                    },
                )

    return []


#
# Pull requests
#
@org_router.get("/pulls/{repo:path}/{pull_number}/changes/{git_commit}")
async def get_pr_changes(
    pull_number: int,
    git_commit: str,
    repo: str,
    notify: Union[int, None] = None,
    user: User = Depends(auth.current_active_user),
):
    user_orgs = get_user_orgs(user)
    org = get_org_with_raise(user_orgs, repo.split("/")[0])
    org_id = org["id"]
    return await _get_pr_changes(pull_number, git_commit, repo, notify, org_id)


@org_router.post("/pulls/{repo:path}/{pull_number}/result/{test_name:path}")
async def add_pr_result(
    test_name: str,
    test_result: TestResults,
    repo: str,
    pull_number: int,
    user: User = Depends(auth.current_active_user),
):
    user_orgs = get_user_orgs(user)
    org = get_org_with_raise(user_orgs, repo.split("/")[0])
    org_id = org["id"]
    return await _add_pr_result(test_name, test_result, repo, pull_number, org_id)


@org_router.delete("/pulls/{repo:path}/{pull_number}")
async def delete_pr_result(
    repo: str,
    pull_number: int,
    user: User = Depends(auth.current_active_user),
):
    """Delete all results for a pull request."""
    user_orgs = get_user_orgs(user)
    org = get_org_with_raise(user_orgs, repo.split("/")[0])
    org_id = org["id"]
    return await _delete_pr_result(repo, pull_number, org_id)


@org_router.get("/pulls/{repo:path}/{pull_number}/result/{test_name:path}")
async def get_pr_result(
    test_name: str,
    repo: str,
    pull_number: int,
    user: User = Depends(auth.current_active_user),
):
    user_orgs = get_user_orgs(user)
    org = get_org_with_raise(user_orgs, repo.split("/")[0])
    org_id = org["id"]
    return await _get_pr_result(test_name, repo, pull_number, org_id)


@org_router.get("/{org_name}/pulls")
async def get_pr_results(org_name: str, user: User = Depends(auth.current_active_user)):
    user_orgs = get_user_orgs(user)
    org = get_org_with_raise(user_orgs, org_name)
    org_id = org["id"]
    return await _get_pr_results(org_id)
