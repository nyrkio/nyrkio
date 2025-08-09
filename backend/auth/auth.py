# Copyright (c) 2024, Nyrkiö Oy

import asyncio
import os
from typing import Optional, Tuple
import logging
import uuid

import httpx
from beanie import PydanticObjectId
from fastapi import Depends, APIRouter, Request, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi_users import BaseUserManager, FastAPIUsers, models, exceptions, schemas
from fastapi_users.db import BeanieUserDatabase, ObjectIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    CookieTransport,
    JWTStrategy,
)
from fastapi_users.exceptions import UserAlreadyExists
from fastapi_users.router.common import ErrorCode

from pydantic import BaseModel

from httpx_oauth.integrations.fastapi import OAuth2AuthorizeCallback
from httpx_oauth.oauth2 import OAuth2Token

from backend.db.db import (
    User,
    get_user_db,
    UserRead,
    UserCreate,
    DBStore,
    UserUpdate,
    OAuthAccount,
)
from backend.auth.github import github_oauth
from backend.auth.email import send_email, read_template_file
from backend.auth.superuser import SuperuserStrategy


async def get_user_manager(user_db: BeanieUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")
COOKIE_NAME = "auth_cookie"
cookie_transport = CookieTransport(cookie_name=COOKIE_NAME)

SECRET = os.environ.get("SECRET_KEY", "fooba")
SERVER_NAME = os.environ.get("SERVER_NAME", "localhost")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=None)


jwt_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

cookie_backend = AuthenticationBackend(
    name="cookie",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)


def get_superuser_strategy() -> SuperuserStrategy:
    return SuperuserStrategy(secret=SECRET, lifetime_seconds=None)


superuser_backend = AuthenticationBackend(
    name="jwt",  # superuser strategy extends jwt
    transport=bearer_transport,
    get_strategy=get_superuser_strategy,
)


fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager, [superuser_backend, cookie_backend]
)

# Github requires this to be the exact same string, so no use trying to switch between
# localhost and staging and prod. (Probably need 3 separate app registrations?)
# REDIRECT_URI = SERVER_NAME + "/api/v0/auth/github/mycallback"
REDIRECT_URI = "https://nyrkio.com/api/v0/auth/github/mycallback"
auth_router = APIRouter(prefix="/auth")
auth_router.include_router(
    fastapi_users.get_oauth_router(
        github_oauth,
        jwt_backend,
        SECRET,
        redirect_url=REDIRECT_URI,
    ),
    prefix="/github",
    tags=["auth"],
)

auth_router.include_router(
    fastapi_users.get_auth_router(jwt_backend, SECRET), prefix="/jwt", tags=["auth"]
)

auth_router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    tags=["auth"],
)

auth_router.include_router(
    fastapi_users.get_verify_router(UserRead),
    tags=["auth"],
)

auth_router.include_router(
    fastapi_users.get_reset_password_router(),
    tags=["auth"],
)

current_active_user = fastapi_users.current_user(active=True)
current_active_superuser = fastapi_users.current_user(active=True, superuser=True)


@auth_router.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}


@auth_router.get("/admin")
async def admin_route(user: User = Depends(current_active_superuser)):
    return {"message": f"Hello admin {user.email}!"}


oauth2_authorize_callback = OAuth2AuthorizeCallback(
    github_oauth, redirect_url=REDIRECT_URI
)


@auth_router.get("/verify-email/{token}")
async def verify_email(
    token: str,
    user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
):
    try:
        user = await user_manager.verify(token, None)
        schema = schemas.model_validate(UserRead, user)
        if user.is_verified:
            return RedirectResponse("/login")
        return schema

    except (exceptions.InvalidVerifyToken, exceptions.UserNotExists):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.VERIFY_USER_BAD_TOKEN,
        )
    except exceptions.UserAlreadyVerified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.VERIFY_USER_ALREADY_VERIFIED,
        )


@auth_router.get("/github/mycallback", include_in_schema=False)
async def github_callback(
    request: Request,
    access_token_state: Tuple[OAuth2Token, str] = Depends(oauth2_authorize_callback),
    user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
):
    token, state = access_token_state
    # Verify that we can decode the token so know it's valid
    # try:
    #     jwt.decode(token, SECRET, audience=[STATE_TOKEN_AUDIENCE], algorithms=["HS256"])
    # except jwt.DecodeError as e:
    #     logging.error(e)
    #     await DBStore().log_json_event(
    #         {
    #             "token": token,
    #             "state": state,
    #             "token_type": repr(type(token)),
    #             "state_type": repr(type(state)),
    #             "token_keys()": list(token.keys()),
    #             "error": repr(e),
    #             "type": "jwt.DecodeError",
    #             "file": "auth.py",
    #             "method": "github_callback",
    #         },
    #         "error",
    #     )
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Couldn't decode Github Oauth response.",
    #     )

    account_id, account_email = await github_oauth.get_id_email(token["access_token"])
    # gh_profile = await github_oauth.get_profile(token["access_token"])
    # print("OAuth2 callback")
    # print(gh_profile)

    if account_email is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.OAUTH_NOT_AVAILABLE_EMAIL,
        )

    try:
        user = await user_manager.oauth_callback(
            github_oauth.name,
            token["access_token"],
            account_id,
            account_email,
            token.get("expires_at"),
            token.get("refresh_token"),
            request,
            associate_by_email=True,
            is_verified_by_default=True,
        )
    except UserAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.OAUTH_USER_ALREADY_EXISTS,
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.LOGIN_BAD_CREDENTIALS,
        )

    # Find all organizations the user is a member of
    client = httpx.AsyncClient()
    response = await client.get(
        "https://api.github.com/user/memberships/orgs",
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )
    if response.status_code != 200:
        logging.error(
            f"Failed to fetch organizations from GitHub: {response.status_code}: {response.text}"
        )
    else:
        orgs = response.json()

        # Find the github account in the user's oauth_accounts
        for account in user.oauth_accounts:
            if (
                account.oauth_name == github_oauth.name
                and account.account_id == account_id
            ):
                account.organizations = orgs

        data = user.oauth_accounts
        update = UserUpdate(oauth_accounts=data)
        user = await user_manager.update(update, user, safe=True)

    # Apparently this should work too / list orgs where Nyrkiö was installed.
    response2 = await client.get(
        "https://api.github.com/user/installations",
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )
    if response.status_code >= 400:
        logging.warn(
            f"Failed to fetch organizations from GitHub/user/installations: {response.status_code}: {response.text}"
        )
    else:
        # TODO: maybe use this later
        logging.debug(response2)

    response = await jwt_backend.login(get_jwt_strategy(), user)
    await user_manager.on_after_login(user, request, response)
    cookie_token = await get_jwt_strategy().write_token(user)
    response = RedirectResponse("/login?gh_login=success&username=" + user.email)
    response.set_cookie(COOKIE_NAME, cookie_token, httponly=True, samesite="strict")
    return response


class UserManager(ObjectIDIDMixin, BaseUserManager[User, PydanticObjectId]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")
        store = DBStore()
        await store.add_default_data(user)

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")
        verify_url = f"{SERVER_NAME}/api/v0/auth/verify-email/{token}"
        msg = read_template_file("verify-email.html", verify_url=verify_url)
        await send_email(user.email, token, "Verify your email", msg)


class SlackCode(BaseModel):
    code: str


@auth_router.post("/slack/oauth")
async def slack_oauth(
    code: SlackCode,
    user: User = Depends(current_active_user),
    user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
):
    store = DBStore()

    logging.info(f"got code {code.code}")
    # Fetch the access token from slack.com
    client = httpx.AsyncClient()
    # redirect_uri = f"https://{SERVER_NAME}/user/settings"
    redirect_uri = "https://nyrkio.com/user/settings"
    logging.info(f"redirect_uri: {redirect_uri}")
    response = await client.post(
        "https://slack.com/api/oauth.v2.access",
        data={
            "client_id": os.environ["SLACK_CLIENT_ID"],
            "client_secret": os.environ["SLACK_CLIENT_SECRET"],
            "code": code.code,
            "redirect_uri": redirect_uri,
        },
    )

    if response.status_code != 200:
        logging.error(
            f"Failed to fetch access token from Slack: {response.status_code}: {response.text}"
        )

    data = response.json()
    logging.info(f"Got response from Slack: {data}")

    if not data["ok"]:
        logging.error(f"Slack returned an error: {data['error']}")
        raise HTTPException(status_code=500, detail="Slack returned an error")

    config = {
        "slack": {
            "team": data["team"]["name"],
            "channel": data["incoming_webhook"]["channel"],
        },
    }

    user.slack = data
    update = UserUpdate(slack=data)
    updated_user = await user_manager.update(update, user, safe=True)

    await store.set_user_config(updated_user.id, config)


async def add_user(username, password, billing=None):
    user = UserCreate(
        email=username,
        password=password,
        is_active=True,
        is_verified=True,
        billing=billing,
    )
    manager = UserManager(BeanieUserDatabase(User, OAuthAccount))
    return await manager.create(user)


async def get_user_by_email(email):
    manager = UserManager(BeanieUserDatabase(User, OAuthAccount))
    return await manager.get_by_email(email)


async def get_user(id):
    manager = UserManager(BeanieUserDatabase(User, OAuthAccount))
    return await manager.get(id)


@auth_router.post("/token")
async def gen_token(user: User = Depends(current_active_user)):
    return await jwt_backend.login(get_jwt_strategy(), user)


class TokenlessSession(BaseModel):
    username: str
    client_secret: str
    server_secret: str


class TokenlessClaim(BaseModel):
    username: str
    client_secret: str

    repo_owner: str
    repo_name: str
    repo_owner_email: Optional[str] = None
    repo_owner_full_name: Optional[str] = None
    workflow_name: str
    event_name: str
    run_number: int
    run_id: int


class TokenlessChallenge(BaseModel):
    session: TokenlessSession
    public_challenge: str
    artifact_id: Optional[str] = None
    public_message: str
    claimed_identity: TokenlessClaim


# TODO: Store in Mongodb some other day ;-)
handshake_ongoing_map = {}
tokenless_users_map = {}


@auth_router.post("/github/tokenless/claim")
async def tokenless_claim(claim: TokenlessClaim) -> TokenlessChallenge:
    """
    First part of a "Tokenless Github Action Authentication Handshake".

    Note that this is like a login end point, so coming here, user is unknown and unauthenticated
    """
    await verify_workflow_run(claim)
    public_challenge, public_message = create_challenge(claim)
    server_secret = create_secret()
    session = TokenlessSession(
        username=claim.username,
        client_secret=claim.client_secret,
        server_secret=server_secret,
    )
    challenge = TokenlessChallenge(
        session=session,
        public_challenge=public_challenge,
        public_message=public_message,
        claimed_identity=claim,
    )
    if session.username not in handshake_ongoing_map:
        handshake_ongoing_map[session.username] = {}
    if session.client_secret in handshake_ongoing_map[session.username]:
        raise HTTPException(
            status_code=409,
            detail=f"This username ({session.username}) and client_secret is already in use by another handshake, or alternatively you mistakenly POSTed the same request twice.",
        )
    handshake_ongoing_map[session.username][session.client_secret] = challenge

    return challenge


@auth_router.post("/github/tokenless/complete")
async def tokenless_complete(
    session: TokenlessSession, artifact_id: int
) -> TokenlessChallenge:
    """
    second part

    Can't trust the incoming data anymore: Just use the username and client secret
    to lookup and match corresponding server_secret.

    The main task is to verify that the public_challenge is found in the artifact file uploaded by
    the client who his claiming the identity of, well essentially claiming to be the process running
    the workflow. We already store the run_id as part of the initial claim, and it is important
    that we stored and will use it as it was supplied as part of the claim. It is the one piece of
    information that solid links the client to the running workflow and therefore with eithr the PR
    author, or repo owner, in the case of a push event.

    Note that to read the file, we also need an artifact_id, which is only now being sent to us.
    We will use it as part of the URL, we have no choice, but note that this id in itself doesn't
    prove anything about anyone's identity. At this point in time there could already be race
    conditions from antagonistic clients, who have read the artifact file already and therefore
    want to pretend they knew the public_challenge, or alternatively, someone might try to
    submit an artifact_id linked to a completely different file in a different workflow.

    In short, the run_id that was stored from the claim, is the one piece of data that we
    have to make sure we are reading a file that must have been written by the PR author /repo owner.
    """

    # Note: user is still unauthenticated as handshake isn't complete. This check is equivalent
    # to checking the session credentials for a logged in user.
    if session.username not in handshake_ongoing_map:
        raise HTTPException(
            status_code=401,
            detail=f"Username {session.username} doesn't have any Tokenless handshakes ongoing.",
        )
    challenge = handshake_ongoing_map[session.username].get(session.client_secret, None)
    if challenge is None:
        # Makes it a bit harder to brute force (but doesn't prevent parallellism)
        await asyncio.sleep(10)
        raise HTTPException(
            status_code=401, detail="Tokenless handshake failed: wrong client_secret"
        )

    challenge.artifact_id = artifact_id
    jwt_token = "TODO"

    if await validate_public_challenge(challenge):
        # If this user doesn't exist at all, create now
        # Create a new short lived JWT token for this user to use for the rest of the workflow run.

        return {
            "message": "Tokenless Handshake completed. Please keep the supplied JWT token secret and use it to authenticate going forward.",
            "github_username": challenge.session.username,
            "jwt_token": jwt_token,
        }
    else:
        return {"message": "Shouldn't happen. You should've already received a 401."}


async def verify_workflow_run(claim: TokenlessClaim):
    client = httpx.AsyncClient()
    uri = f"https://api.github.com/repos/{claim.repo_owner}/{claim.repo_name}/actions/runs/{claim.run_id}"
    # TODO: We can also support private repos, need to supply our github app token
    # headers={"Authorization": f"Bearer {token['access_token']}"},)
    response = await client.get(uri)
    if response.status_code != 200:
        logging.error(
            f"TokenlessHandshake: Failed to fetch the given workflow run from GitHub: {response.status_code}: {response.text}"
        )
        logging.error(dict(claim))
        raise HTTPException(
            status_code=424,
            detail=f"TokenlessHandshake: Could not find the Github workflow you claim to be running: {uri}",
        )
    # For pull requests, username is not the same as repo owner, so check that (for both, while at it)
    workflow = response.json()
    # TODO: Debug - remove later
    print(workflow)
    if workflow["event"] == "pull_request":
        workflow_username = workflow["actor"]["login"]
        if workflow_username != claim.username:
            logging.error(
                f"TokenlessHandshake failed: claim has username {claim.username} and PR has {workflow_username}"
            )
            raise HTTPException(
                status_code=401,
                detail=f"TokenlessHandshake failed. You claimed to be github user {claim.username} but that was not confirmed by {uri}",
            )

    if workflow["event"] == "push":
        workflow_username = workflow["repository"]["owner"]["login"]
        if workflow_username != claim.username:
            logging.error(
                f"TokenlessHandshake failed: claim has username {claim.username} and PR has {workflow_username}"
            )
            raise HTTPException(
                status_code=401,
                detail=f"TokenlessHandshake failed. You claimed to be github user {claim.username} but that was not confirmed by {uri}",
            )


def create_secret() -> str:
    return str(uuid.uuid4())


def create_challenge(claim: TokenlessClaim) -> str:
    randomstr = str(uuid.uuid4())
    workflowstr = f"/{claim.repo_owner}/{claim.repo_name}/actions/runs/{claim.run_id}"

    line1 = "TokenlessHandshake between github.com and nyrkio.com:\n"
    line2 = f"I am {claim.username} and this is proof that I am currently running {workflowstr}: {randomstr}"

    return randomstr, line1 + line2


async def validate_public_challenge(challenge: TokenlessChallenge) -> bool:
    artifact_url = f"https://api.github.com/{challenge.claim.repo_owner}/{challenge.claim.repo_name}/actions/runs/{challenge.claim.run_id}/artifacts/{challenge.artifact_id}"
    logging.info(f"GET: {artifact_url}")
    client = httpx.AsyncClient()
    response = await client.get(artifact_url)
    if response.status_code != 200:
        logging.error(
            f"TokenlessHandshake: Failed to fetch the given artifact file from GitHub: {response.status_code}: {response.text}"
        )
        raise HTTPException(
            status_code=424,
            detail=f"TokenlessHandshake: Could not find the artifact fail you should have published in your github action: {artifact_url}",
        )
    artifact_contents = response.data
    if artifact_contents.find(challenge.public_message) and artifact_contents.find(
        challenge.public_challenge
    ):
        logging.debug(
            f"Successful TokenlessHandshake for {challenge.session.username}. Now creating a JWT token they can use going forward."
        )
        return True
    else:
        raise HTTPException(
            status_code=401,
            detail=f"Artifact file {artifact_url} did not contain the public challenge: {challenge.public_challenge}. For security, we will delete your initial claim and challenge now. Please start again from scratch.",
        )
