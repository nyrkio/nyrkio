import asyncio
from datetime import datetime
from backend.auth import auth
from backend.auth.common import get_user_manager
from backend.db.db import get_user_db, DBStore, MockDBStrategy

from fastapi import Depends


def test_test_user_can_login(client):
    client.login()


def test_invalid_user_cannot_login(unauthenticated_client):
    response = unauthenticated_client.post(
        "/api/v0/auth/jwt/login", data={"username": "bad@foo.com", "password": "foo"}
    )
    # should this be HTTP 401?
    assert response.status_code == 400


def test_create_new_user(unauthenticated_client):
    email = "newuser@foo.com"
    password = "somepass"
    headers = {"Content-type": "application/json"}
    response = unauthenticated_client.post(
        "/api/v0/auth/register",
        headers=headers,
        json={"email": email, "password": password},
    )
    assert response.status_code == 201


def test_get_user_by_email():
    email = "blah@foo.com"
    user = asyncio.run(auth.add_user(email, "foo"))
    u = asyncio.run(auth.get_user_by_email(email))
    assert user == u


def undepend(d):
    return unasync(d.dependency)


def unasync(ag):
    async def unasync_iter(ag_a):
        print(ag_a)
        async for sf in ag_a:
            return sf

    return asyncio.run(unasync_iter(ag))


def test_sso_groups_created():
    user_db_dep = Depends(get_user_db())
    print(vars(user_db_dep))
    user_db = undepend(user_db_dep)
    print(user_db)
    user_manager_dep = Depends(get_user_manager(user_db))
    print(vars(user_manager_dep))
    user_manager = undepend(user_manager_dep)
    print(vars(user_manager))
    print(user_manager.user_db)
    print(vars(user_manager.user_db))
    print(user_manager.user_db.store)
    print(vars(user_manager.user_db.store))

    store = DBStore()
    strategy = MockDBStrategy()
    store.setup(strategy)
    print(vars(user_manager.user_db.store))
    # store.strategy = strategy
    # print(vars(user_manager.user_db.store))
    asyncio.run(store.startup())
    print(vars(user_manager.user_db.store))
    # store.strategy = strategy
    # print(vars(user_manager.user_db.store))

    user_manager.user_db.store = store
    print(vars(user_manager.user_db.store))
    print("-----------------------------")

    # user_manager.user_db.store.setup( MockDBStrategy())
    # user_manager.user_db.store.strategy = MockDBStrategy()
    # print(vars(user_manager.user_db.store))
    # user_manager.user_db.store.strategy.connect()
    # print(vars(user_manager.user_db.store))
    # asyncio.run(user_manager.user_db.store.startup())
    # user_manager.user_db.store.setup( MockDBStrategy())
    # user_manager.user_db.store.strategy = MockDBStrategy()
    # # asyncio.run(user_manager.user_db.store.strategy.init_db())
    # print(vars(user_manager.user_db.store))
    #

    db = user_manager.user_db.store.db
    ssoprovider = {
        "oauth_issuer": "onelogin_for_test",
        "org_name": "Test",
        "org_contact_email": "test@example.com",
        "org_domain": "example.com",
        "github_org_map": ["test_gh_org"],
        "oauth_full_domain": "test.example.com",
        "oauth_tld": "example.com",
        "scopes": ["openid", "profile", "groups"],
        "secrets": {
            "client_id": "abc",
            "client_secret": "123",
            "well_known_config": "https://test.example.com/oidc/2/.well-known/openid-configuration",
        },
    }
    asyncio.run(db.sso.insert_one(ssoprovider))
    sso_config = asyncio.run(
        user_manager.user_db.store.db.sso.find().to_list()
    )  # get_sso_config()#oauth_full_domain=oauth_name)
    print(sso_config)

    exp = int(datetime.now().timestamp() + 100)
    fut = user_manager.oauth_callback(
        oauth_name="test.example.com",
        access_token="abcdef12345",
        account_id="255509999",
        account_email="sso_user2@example.com",
        expires_at=exp,
        refresh_token="8ef8e5aa",
        associate_by_email=False,
    )
    user = asyncio.run(fut)
    print(vars(user))
    u = asyncio.run(store.get_user_without_any_fastapi_nonsense(user.id))
    print(u)
    assert u["email"] == "sso_user2@example.com"
    assert u["oauth_accounts"][0]["organizations"][0]["login"] == "test_gh_org"
