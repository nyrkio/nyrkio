import logging
import os

from fastapi import Depends, APIRouter, HTTPException, status
from httpx import AsyncClient

from backend.auth.auth import get_current_active_user
from backend.db.db import User, DBStore

CLIENT_ID = "Iv1.829e5507d1b06795"
CLIENT_SECRET = os.environ.get("GITHUB_CLIENT_SECRET", None)

github_router = APIRouter()
@github_router.get("/github")
async def github_login(code):
    if not CLIENT_SECRET:
        logging.error("Github client secret not set")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Unable to authenticate with Github")

    logging.error(f"Received code {code}")
    async with AsyncClient() as client:
        response = await client.post("https://github.com/login/oauth/access_token",
                                    headers={"Accept": "application/json"},
                                    params={
                                         "client_id": CLIENT_ID,
                                         "client_secret": CLIENT_SECRET,
                                         "code": code
                                    })
        # ensure response is 200
        response.raise_for_status()
        # extract json payload from response
        json = response.json()
        if not "access_token" in json:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid access token")

        access_token = json["access_token"]
        # Fetch user details from github API
        response = await client.get("https://api.github.com/user",
                                    headers={"Authorization": f"Bearer {access_token}"})
        response.raise_for_status()
        json = response.json()

    username = json["login"]
    email = json["email"]
    full_name = json["name"]

    user = User(username=username, email=email, full_name=full_name)
    store = DBStore()
    store.add_user(user)

    return {"access_token": access_token, "token_type": "bearer"}
