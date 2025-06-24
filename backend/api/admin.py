import logging
import sys
from typing import Dict, List
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi_users.exceptions import UserNotExists

from backend.auth import auth
from backend.db.db import User, DBStore
from backend.auth.superuser import superuser_active_map

from pydantic import BaseModel

admin_router = APIRouter(prefix="/admin")
logging_out = logging.StreamHandler(stream=sys.stdout)
logging_out.setLevel(logging.INFO)
root_logger = logging.getLogger()
root_logger.addHandler(logging_out)


@admin_router.get("/all_users")
async def all_users(user: User = Depends(auth.current_active_superuser)) -> List[Dict]:
    logging.info(f"Admin {user.email} requested all users")
    store = DBStore()
    results = await store.get_all_users()
    return results


class ImpersonateLogin(BaseModel):
    username: str
    # Not actually used:
    id: str


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

    test_name = "/".join(test_path.split("/")[1:])

    from backend.api.api import calc_changes

    return await calc_changes(test_name, user.id)


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
    results, _ = await store.get_results(user.id, test_name)
    return results


@admin_router.post("/impersonate")
async def impersonate(
    data: ImpersonateLogin, user: User = Depends(auth.current_active_superuser)
) -> Dict:
    logging.info(f"Admin {user.email} requested to impersonate {data.username}")
    fa_user = await auth.get_user_by_email(data.username)
    if not str(fa_user.id) == data.id:
        print(fa_user)
        raise ValueError(
            "id fields for the user you asked to impersonate doesn't match. ({} {})".format(
                data.username, data.id
            )
        )

    datetime.now(timezone.utc) + timedelta(seconds=2 * 3600)

    # store = DBStore()
    # await store.set_impersonate_user(admin_user=user, impersonate_user=fa_user, expire=expire)
    superuser_active_map[user.email] = fa_user
    return_user = {
        "user_id": str(fa_user.id),
        "user_email": data.username,
        "superuser": {"user_email": user.email},
    }

    return return_user


@admin_router.get("/impersonate")
async def impersonate_get(user: User = Depends(auth.current_active_user)) -> Dict:
    # store = DBStore()
    # await store.get_impersonate_user(admin_user=user)
    return_user = {
        "user_id": str(user.id),
        "user_email": user.email,
    }
    if user.superuser and "user_email" in user.superuser:
        return_user["superuser"] = {
            "user_email": user.superuser["user_email"],
        }
    return return_user


@admin_router.delete("/impersonate")
async def impersonate_delete(user: User = Depends(auth.current_active_user)) -> Dict:
    if (
        user
        and user.superuser
        and "user_email" in user.superuser
        and user.superuser["user_email"] in superuser_active_map
    ):
        del superuser_active_map[user.superuser["user_email"]]
        # store = DBStore()
        # await store.delete_impersonate_user(admin_user=user, impersonate_user=fa_user, expire=expire)
    return_user = {}
    if user.superuser and "user_email" in user.superuser:
        return_user = {
            "user_email": user.superuser["user_email"],
            "yourself": True,
        }

    return return_user
