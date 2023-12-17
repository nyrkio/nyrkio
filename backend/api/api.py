# Copyright (c) 2024, Nyrkiö Oy

from collections import defaultdict
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, APIRouter, Depends, HTTPException
from pydantic import BaseModel, RootModel

from backend.auth import auth
from backend.db.db import User

app = FastAPI()

app.include_router(auth.auth_router)


api_router = APIRouter(prefix="/api/v0")


temp_db = defaultdict(list)


@api_router.get("/results")
async def results(user: User = Depends(auth.current_active_user)):
    return temp_db


@api_router.get("/result/{test_name}")
async def get_result(test_name: str, user: User = Depends(auth.current_active_user)):
    if test_name not in temp_db:
        raise HTTPException(status_code=404, detail="Not Found")
    return temp_db[test_name]


class TestResult(BaseModel):
    timestamp: int
    metrics: Optional[Dict]
    attributes: Optional[Dict]

class TestResults(RootModel[Any]):
    root: List[TestResult]


@api_router.post("/result/{test_name}")
async def add_result(
    test_name: str, data: TestResults, user: User = Depends(auth.current_active_user)
):
    temp_db[test_name] += data.root
    return {}


# Must come at the end, once we've setup all the routes
app.include_router(api_router)


@app.on_event("startup")
async def do_db():
    from backend.db.db import do_on_startup

    await do_on_startup()
