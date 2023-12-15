# Copyright (c) 2024, Nyrkiö Oy


from fastapi import FastAPI, APIRouter, Depends

from backend.auth import auth
from backend.db.db import User

app = FastAPI()

app.include_router(auth.auth_router)


api_router = APIRouter(prefix="/api/v0")


@api_router.get("/results")
async def results(user: User = Depends(auth.current_active_user)):
    return {}


# Must come at the end, once we've setup all the routes
app.include_router(api_router)


@app.on_event("startup")
async def do_db():
    from backend.auth.auth import do_on_startup

    await do_on_startup()
