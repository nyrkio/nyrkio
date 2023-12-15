import logging
from fastapi import Depends, APIRouter, HTTPException, status
from httpx import AsyncClient

from backend.auth.auth import get_current_active_user
from backend.db.db import User

CLIENT_ID = "Iv1.829e5507d1b06795"
CLIENT_SECRET = "b33fa30dd894ecb1e8fd229c7653861370713bff"

github_router = APIRouter()
@github_router.get("/github")
async def github_login(code):
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
        logging.error(json)
        username = json["login"]
        email = json["email"]
        full_name = json["name"]

        # Create a new User object
        user = User(username=username, email=email, full_name=full_name)
        # Store the user in the database
        db_add_or_update_user(user)


    return {}