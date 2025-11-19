# Copyright (c) 2024, Nyrkiö Oy

import os
from typing import Tuple
import logging
import uuid

import httpx

# from fastapi import Depends, APIRouter, Request, HTTPException, status
from fastapi import Depends, Request, HTTPException, status, APIRouter
from fastapi.responses import RedirectResponse
from fastapi_users import BaseUserManager, FastAPIUsers, models, exceptions, schemas
from fastapi_users.db import BeanieUserDatabase
from fastapi_users.authentication import (
    AuthenticationBackend,
    CookieTransport,
)
from fastapi_users.exceptions import UserAlreadyExists
from fastapi_users.router.common import ErrorCode

from pydantic import BaseModel

from httpx_oauth.integrations.fastapi import OAuth2AuthorizeCallback
from httpx_oauth.oauth2 import OAuth2Token

from backend.db.db import (
    User,
    UserRead,
    UserCreate,
    DBStore,
    UserUpdate,
    OAuthAccount,
)
from backend.auth.github import github_oauth
from backend.auth.onelogin import (
    CLIENT_SECRET as ONELOGIN_CLIENT_SECRET,
    OneLoginOAuth2,
)
from backend.auth.superuser import SuperuserStrategy

from backend.auth.common import (
    UserManager,
    get_user_manager,
    jwt_backend,
    get_jwt_strategy,
    bearer_transport,
)


COOKIE_NAME = "auth_cookie"
cookie_transport = CookieTransport(cookie_name=COOKIE_NAME)

SECRET = os.environ.get("SECRET_KEY", "fooba")
SERVER_NAME = os.environ.get("SERVER_NAME", "localhost")

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", None)
HTTP_HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"}


sso_secrets = {"onelogin": ONELOGIN_CLIENT_SECRET}

cookie_backend = AuthenticationBackend(
    name="cookie",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)

auth_router = APIRouter(prefix="/auth")


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


# auth_router = APIRouter(prefix="/auth")
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
current_user_token = fastapi_users.authenticator.current_user_token(active=True)


@auth_router.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}


@auth_router.get("/admin")
async def admin_route(user: User = Depends(current_active_superuser)):
    return {"message": f"Hello admin {user.email}!"}


github_oauth2_authorize_callback = OAuth2AuthorizeCallback(
    github_oauth, redirect_url=REDIRECT_URI
)

sso_oauth2_authorize_callbacks = {}
sso_routers = {}


@auth_router.post("/start/sso/login")
async def start_sso_login(
    oauth_my_domain: str,
    oauth_tld: str,
):
    store = DBStore()
    oauth_full_domain = oauth_my_domain + "." + oauth_tld
    oauth_config = store.get_sso_config(oauth_full_domain=oauth_full_domain)
    if not oauth_config:
        raise HTTPException(
            status_code=404,
            detail=f"Not found: {oauth_full_domain} is not configured as a known SSO issuer for Nyrkiö. To add your SSO to Nyrkiö, please contact sales@nyrkio.com",
        )

    if len(oauth_config) > 1:
        raise HTTPException(
            status_code=500,
            detail=f"Found more than one SSO issuer for {oauth_full_domain}. This is an error on our side and I don't know how to continue. I'm truly sorry about this.",
        )

    _dynamic_sso_callback_setup(oauth_full_domain, oauth_config)
    oauth_issuer = oauth_config["oauth_issuer"]
    return {"next_url": f"/api/v0/auth/{oauth_issuer}/authorize"}


async def _dynamic_sso_callback_setup(oauth_full_domain, oauth_config):
    oauth_issuer = oauth_config["oauth_issuer"]
    redirect_url = (
        f"https://staging.nyrkio.com/api/v0/auth/sso/{oauth_issuer}/mycallback"
    )
    if oauth_issuer not in sso_oauth2_authorize_callbacks:
        sso_oauth = OneLoginOAuth2(
            sso_domain=oauth_full_domain,
            scopes=oauth_config["scopes"],
        )

        sso_oauth2_authorize_callback = OAuth2AuthorizeCallback(
            sso_oauth,
            redirect_url=redirect_url,
        )
        sso_oauth2_authorize_callbacks[oauth_issuer] = sso_oauth2_authorize_callback
        sso_router = fastapi_users.get_oauth_router(
            sso_oauth,
            jwt_backend,
            sso_secrets[oauth_issuer],
            redirect_url=redirect_url,
        )

        @sso_router.get("/mycallback", include_in_schema=False)
        async def sso_callback(
            request: Request,
            access_token_state: Tuple[OAuth2Token, str] = Depends(
                sso_oauth2_authorize_callback
            ),
            user_manager: BaseUserManager[models.UP, models.ID] = Depends(
                get_user_manager
            ),
        ):
            _sso_mycallback_handler(
                oauth_full_domain, sso_oauth, request, access_token_state, user_manager
            )

        auth_router.include_router(
            sso_router,
            prefix=f"/sso/{oauth_issuer}",
            tags=["auth"],
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
            status_code=status.HTTP_409_CONFLICT,
            detail=ErrorCode.VERIFY_USER_ALREADY_VERIFIED,
        )


@auth_router.get("/github/mycallback", include_in_schema=False)
async def github_callback(
    request: Request,
    access_token_state: Tuple[OAuth2Token, str] = Depends(
        github_oauth2_authorize_callback
    ),
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
    # This seems to never happen? If it did, wouldn't we at this point then just .get() the user and consider them logged in?
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


async def _sso_mycallback_handler(
    oauth_full_domain, sso_oauth, request, access_token_state, user_manager
):
    token, state = access_token_state
    account_id, account_email = await sso_oauth.get_id_email(token["access_token"])
    if account_email is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.OAUTH_NOT_AVAILABLE_EMAIL,
        )

    try:
        user = await user_manager.oauth_callback(
            "onelogin",
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
            detail="This user is deactivated at nyrkio.com",
        )

    userinfo = await sso_oauth.get_userinfo(token["access_token"])

    for oauth_acct in user.oauth_accounts:
        if oauth_acct.oauth_name != "onelogin":
            print("skip", oauth_acct)
            continue
        if oauth_acct.account_email != account_email:
            print("Someone screwed up")
            print(account_email, oauth_acct.email)
            raise HTTPException(
                status_code=500,
                detail="This should never happen",
            )

        oauth_acct.organizations = []
        oauth_acct.organizations.append(userinfo)

    update = UserUpdate(oauth_accounts=user.oauth_accounts)
    user = await user_manager.update(update, user, safe=True)

    response = await jwt_backend.login(get_jwt_strategy(), user)
    await user_manager.on_after_login(user, request, response)
    cookie_token = await get_jwt_strategy().write_token(user)
    response = RedirectResponse("/login?onelogin_login=success&username=" + user.email)
    response.set_cookie(COOKIE_NAME, cookie_token, httponly=True, samesite="strict")
    return response


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
