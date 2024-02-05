from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.auth import auth
from backend.db.db import User, DBStore

user_router = APIRouter(prefix="/user")


class Notifiers(BaseModel):
    slack: bool


class UserConfig(BaseModel):
    notifiers: Notifiers


@user_router.get("/config")
async def get_user_config(user: User = Depends(auth.current_active_user)):
    store = DBStore()
    config = await store.get_user_config(user)
    return config


@user_router.post("/config")
async def set_user_config(
    config: UserConfig, user: User = Depends(auth.current_active_user)
):
    store = DBStore()
    await store.set_user_config(user, config.model_dump())


@user_router.put("/config")
async def update_user_config(
    config: UserConfig, user: User = Depends(auth.current_active_user)
):
    store = DBStore()
    json = config.model_dump()
    await store.set_user_config(user, json)


@user_router.delete("/config")
async def delete_user_config(user: User = Depends(auth.current_active_user)):
    store = DBStore()
    await store.delete_user_config(user)
