# Copyright (c) 2024, Nyrkiö Oy

from fastapi import FastAPI

from . import api, auth

app = FastAPI()

app.include_router(api.router)
app.include_router(auth.token_router)
app.include_router(auth.user_router)


@app.get("/")
async def root():
    return {}
