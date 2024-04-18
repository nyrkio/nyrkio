from typing import Dict, List, Any

from pydantic import BaseModel, RootModel
from fastapi import APIRouter, Depends, HTTPException

from backend.auth import auth
from backend.db.db import User, DBStore
from backend.api.public import build_public_test_name

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
    config = await store.get_test_config(user.id, test_name)
    return config


class TestConfigList(RootModel[Any]):
    root: List[TestConfig]


@config_router.post("/config/{test_name:path}")
async def set_config(
    test_name: str, data: TestConfigList, user: User = Depends(auth.current_active_user)
) -> Dict:
    """
    If the config is adding a public test (by setting the "public" key to True),
    we check if the test name is already in use by another user.  If it is,
    raise a HTTP 409 exception. When an exception is raised, none of the
    configuration changes are made.
    """
    store = DBStore()

    # TODO(mfleming) This is an attempt to avoid an abstraction leak. The DB
    # layer deals with core Python types and internal objects, but the API
    # layer can deal with Pydantic models.
    #
    # Reconsider whether this is the best approach sometime in the future.
    configs = [elem.model_dump() for elem in data.root]

    public_tests = await store.get_public_results()
    public_test_names = [build_public_test_name(p) for p in public_tests]

    for c in configs:
        conf = dict(c)
        conf["user_id"] = user.id
        conf["test_name"] = test_name
        name = build_public_test_name(conf)
        if conf["public"] and name in public_test_names:
            raise HTTPException(
                status_code=409, detail=f"Public test already exists for {name}"
            )

    await store.set_test_config(user.id, test_name, configs)
    return {}


@config_router.delete("/config/{test_name:path}")
async def delete_config(
    test_name: str, user: User = Depends(auth.current_active_user)
) -> Dict:
    store = DBStore()
    await store.delete_test_config(user.id, test_name)
    return {}
