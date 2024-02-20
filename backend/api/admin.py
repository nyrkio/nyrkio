import logging
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException
from fastapi_users.exceptions import UserNotExists

from backend.auth import auth
from backend.core.config import Config
from backend.db.db import User, DBStore

admin_router = APIRouter(prefix="/admin")


@admin_router.get("/results")
async def results(user: User = Depends(auth.current_active_superuser)) -> Dict:
    logging.info(f"Admin {user.email} requested all results")
    store = DBStore()
    results = await store.get_test_names()
    updated_results = {}
    for k, v in results.items():
        updated_results[k] = [{"test_name": name} for name in v]

    return updated_results


@admin_router.get("/result/{test_path:path}/changes")
async def changes(test_path: str, user: User = Depends(auth.current_active_superuser)):
    logging.info(f"Admin {user.email} requested changes for {test_path}")

    user_email = test_path.split("/")[0]
    try:
        user = await auth.get_user_by_email(user_email)
    except UserNotExists:
        raise HTTPException(status_code=404, detail="No such user exists")

    store = DBStore()
    test_name = "/".join(test_path.split("/")[1:])
    results = await store.get_results(user, test_name)
    disabled = await store.get_disabled_metrics(user, test_name)

    config = await store.get_user_config(user)
    config = config.get("core", None)
    if config:
        config = Config(**config)

    from backend.api.api import calc_changes

    return await calc_changes(test_name, results, disabled, config)


@admin_router.get("/result/{test_path:path}")
async def get_result(
    test_path: str, user: User = Depends(auth.current_active_superuser)
) -> List[Dict]:
    logging.info(f"Admin {user.email} requested results for {test_path}")

    # Extract the user email from the first component in test_path
    user_email = test_path.split("/")[0]
    try:
        user = await auth.get_user_by_email(user_email)
    except UserNotExists:
        raise HTTPException(status_code=404, detail="No such user exists")

    store = DBStore()
    test_name = "/".join(test_path.split("/")[1:])
    return await store.get_results(user, test_name)
