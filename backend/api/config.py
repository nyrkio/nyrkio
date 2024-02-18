from typing import Dict, List, Any

from pydantic import BaseModel, RootModel
from fastapi import APIRouter, Depends, HTTPException

from backend.auth import auth
from backend.db.db import User, DBStore, DBStoreResultExists

config_router = APIRouter()


class TestConfigAttributes(BaseModel):
    git_repo: str
    branch: str


class TestConfig(BaseModel):
    public: bool
    attributes: TestConfigAttributes


@config_router.get("/config/{test_name:path}")
async def get_config(
    test_name: str, user: User = Depends(auth.current_active_user)
) -> List[Dict]:
    store = DBStore()
    config = await store.get_test_config(user, test_name)
    return config


class TestConfigList(RootModel[Any]):
    root: List[TestConfig]


def extract_public_test_name(attributes):
    # TODO(mfleming) we assume a https://github.com repo
    name = attributes["git_repo"].replace("https://github.com/", "")
    name += "/" + attributes["branch"]
    return name


@config_router.post("/config/{test_name:path}")
async def set_config(
    test_name: str, data: TestConfigList, user: User = Depends(auth.current_active_user)
) -> Dict:
    store = DBStore()

    # TODO(mfleming) This is an attempt to avoid an abstraction leak. The DB
    # layer deals with core Python types and internal objects, but the API
    # layer can deal with Pydantic models.
    #
    # Reconsider whether this is the best approach sometime in the future.
    configs = [elem.model_dump() for elem in data.root]

    await store.set_test_config(user, test_name, configs)

    # Update the public results map
    for c in configs:
        public_test_name = extract_public_test_name(c["attributes"]) + "/" + test_name
        import logging

        logging.info(
            f"Setting up public map for {public_test_name} and {user} and {c['public']}"
        )
        try:
            await store.set_public_map(public_test_name, user, c["public"])
        except DBStoreResultExists:
            raise HTTPException(status_code=409, detail="Public test already exists")

    return {}
