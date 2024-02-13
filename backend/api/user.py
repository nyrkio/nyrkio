from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.auth import auth
from backend.db.db import User, DBStore

user_router = APIRouter(prefix="/user")


class Notifiers(BaseModel):
    slack: bool


class Core(BaseModel):
    """
    Configuration params for the core of Nyrkiö.

    Note that no values are optional, so the user must provide both
    min_magnitude and max_pvalue if they want to update the config.
    """

    min_magnitude: float
    max_pvalue: float


class UserConfig(BaseModel):
    notifiers: Optional[Notifiers] = None
    core: Optional[Core] = None


def validate_config(config: UserConfig):
    """Provide extra validation for the UserConfig model that Pydantic can't handle."""
    if config.core is not None and config.core.max_pvalue > 1.0:
        raise HTTPException(
            status_code=400, detail="max_pvalue must be less than or equal to 1.0"
        )


@user_router.get("/config")
async def get_user_config(user: User = Depends(auth.current_active_user)):
    store = DBStore()
    config = await store.get_user_config(user)
    return config


@user_router.post("/config")
async def set_user_config(
    config: UserConfig, user: User = Depends(auth.current_active_user)
):
    validate_config(config)
    store = DBStore()
    await store.set_user_config(user, config.model_dump())


@user_router.put("/config")
async def update_user_config(
    config: UserConfig, user: User = Depends(auth.current_active_user)
):
    validate_config(config)

    store = DBStore()
    json = config.model_dump()
    await store.set_user_config(user, json)


@user_router.delete("/config")
async def delete_user_config(user: User = Depends(auth.current_active_user)):
    store = DBStore()
    await store.delete_user_config(user)
