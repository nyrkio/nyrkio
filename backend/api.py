# Copyright (c) 2024, Nyrkiö Oy

from typing_extensions import Annotated

from fastapi import APIRouter, Depends

from .auth import oauth2_scheme

router = APIRouter(prefix="/api/v0")


@router.get("/results")
async def results(token: Annotated[str, Depends(oauth2_scheme)]):
    return {}
