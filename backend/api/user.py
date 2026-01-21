from typing import Optional, Dict
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.auth import auth
from backend.db.db import User, DBStore
from backend.api.metered import query_meter_consumption

user_router = APIRouter(prefix="/user")


class Notifiers(BaseModel):
    slack: bool
    github: bool
    since_days: int
    github_pr: Optional[bool] = None


class Core(BaseModel):
    """
    Configuration params for the core of Nyrkiö.

    Note that no values are optional, so the user must provide both
    min_magnitude and max_pvalue if they want to update the config.
    """

    min_magnitude: float
    max_pvalue: float


class Billing(BaseModel):
    plan: str


class GitHubConfig(BaseModel):
    """
    Holds the json received by /github/webhook when user installed Nyrkiö as a GitHub app
    """

    # The app config has lots of stuff so don't even try to lock down more than it's a json object
    app: Dict


class UserConfig(BaseModel):
    notifiers: Optional[Notifiers] = None
    core: Optional[Core] = None
    billing: Optional[Billing] = None
    billing_runners: Optional[Billing] = None
    github: Optional[GitHubConfig] = None


def validate_config(config: UserConfig):
    """Provide extra validation for the UserConfig model that Pydantic can't handle."""
    if config.core is not None and config.core.max_pvalue > 1.0:
        raise HTTPException(
            status_code=400, detail="max_pvalue must be less than or equal to 1.0"
        )

    if config.billing is not None:
        raise HTTPException(status_code=400, detail="You cannot set billing plan")
    if config.billing_runners is not None:
        raise HTTPException(status_code=400, detail="You cannot set billing plan")

    if config.github is not None:
        raise HTTPException(status_code=400, detail="You cannot set github app config")


@user_router.get("/config")
async def get_user_config(user: User = Depends(auth.current_active_user)):
    store = DBStore()
    config, _ = await store.get_user_config(user.id)

    config["billing"] = {"plan": user.billing["plan"]} if user.billing else None
    config["billing_runners"] = (
        {"plan": user.billing_runners["plan"]} if user.billing_runners else None
    )

    return config


# Note: Someone was lazy and under the hood we do an upsert both for post and put
@user_router.post("/config")
async def set_user_config(
    config: UserConfig, user: User = Depends(auth.current_active_user)
):
    # print("Incoming UserConfig parsed as:")
    # print(config.model_dump())
    # print(user.model_dump())
    if user.is_cph_user:
        raise HTTPException(
            status_code=403,
            detail="You cannot set configuration options when using the light weight Challenge Response Handshake. Please sign in properly at nyrkio.com and then supply a JWT Token for authentication.",
        )

    validate_config(config)
    store = DBStore()
    await store.set_user_config(user.id, config.model_dump())


@user_router.put("/config")
async def update_user_config(
    config: UserConfig, user: User = Depends(auth.current_active_user)
):
    if user.is_cph_user:
        raise HTTPException(
            status_code=403,
            detail="You cannot set configuration options when using the light weight Challenge Response Handshake. Please sign in properly at nyrkio.com and then supply a JWT Token for authentication.",
        )

    validate_config(config)

    store = DBStore()
    json = config.model_dump()
    await store.set_user_config(user.id, json)


@user_router.delete("/config")
async def delete_user_config(user: User = Depends(auth.current_active_user)):
    if user.is_cph_user:
        raise HTTPException(
            status_code=403,
            detail="You cannot set configuration options when using the light weight Challenge Response Handshake. Please sign in properly at nyrkio.com and then supply a JWT Token for authentication.",
        )
    store = DBStore()
    await store.delete_user_config(user.id)


@user_router.get("/meters")
async def get_strip(user: User = Depends(auth.current_active_user)) -> Dict:
    if user.billing_runners:
        customer_id = user.billing_runners.get("customer_id")
        return query_meter_consumption(customer_id)
    else:
        return {}
