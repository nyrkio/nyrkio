# Copyright (c) 2024, Nyrkiö Oy

from typing_extensions import Annotated

from fastapi import FastAPI, APIRouter, Depends

from ..auth import auth
from ..auth.auth import oauth2_scheme

app = FastAPI()

app.include_router(auth.token_router)
app.include_router(auth.user_router)


api_router = APIRouter(prefix="/api/v0")

@api_router.get("/results")
async def results(token: Annotated[str, Depends(oauth2_scheme)]):
    return {}

# Must come at the end, once we've setup all the routes
app.include_router(api_router)
