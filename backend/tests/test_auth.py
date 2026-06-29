import asyncio
from datetime import datetime
import pytest

from backend.auth import auth
from backend.auth.common import get_user_manager
from backend.db.db import get_user_db, DBStore, MockDBStrategy

from fastapi import Depends
from fastapi_users.exceptions import UserAlreadyExists


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
        "allowed_github_orgs": [
            {"login": "test_gh_org", "id": 901},
            {"login": "another_org", "id": 902},
        ],
        "oauth_full_domain": "test.example.com",
        "oauth_tld": "example.com",
        "scopes": ["openid", "profile", "groups"],
        "secrets": {
            "client_id": "abc",
            "client_secret": "123",
            "well_known_config": "https://test.example.com/oidc/2/.well-known/openid-configuration",
        },
    }
    ssoprovider2 = {
        "oauth_issuer": "onelogin_for_test2",
        "org_name": "Test2",
        "org_contact_email": "test2@example.com",
        "org_domain": "example.com",
        "allowed_github_orgs": [
            {"login": "test_gh_org2", "id": 901},
            {"login": "another_org", "id": 902},
        ],
        "oauth_full_domain": "test2.example.com",
        "oauth_tld": "example.com",
        "scopes": ["openid", "profile", "groups"],
        "secrets": {
            "client_id": "abc",
            "client_secret": "123",
            "well_known_config": "https://test.example.com/oidc/2/.well-known/openid-configuration",
        },
    }
    asyncio.run(db.sso.insert_one(ssoprovider))
    asyncio.run(db.sso.insert_one(ssoprovider2))
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
    # {
    #     'email': 'sso_user2@example.com',
    #     'hashed_password': '$2b$12$08Jb.V8vWWg/6jjepS8SW.BIlKoFzdbTYER41bZv7YuZoqPXc1CQe',
    #     'is_active': True,
    #     'is_superuser': False,
    #     'is_verified': False,
    #     'oauth_accounts': [
    #         {'id': ObjectId('6a3e967a2b4ccd43c982485b'),
    #          'oauth_name': 'test.example.com',
    #          'access_token': 'abcdef12345',
    #          'account_id': '255509999',
    #          'account_email': 'sso_user2@example.com',
    #          'expires_at': 1782486750,
    #          'refresh_token': '8ef8e5aa',
    #          'organizations': [
    #              {'url': 'https://test.example.com/orgs/test_gh_org',
    #               'state': 'active',
    #               'role': 'user',
    #               'organization_url': 'https://test.example.com/orgs/test_gh_org',
    #               'organization':
    #                   {
    #                       'login': 'test_gh_org',
    #                       'id': 900,
    #                       'url': 'https://test.example.com/orgs/test_gh_org',
    #                       'repos_url': 'https://api.github.com/orgs/test_gh_org/repos',
    #                       'description': 'Group is created and managed by Nyrkiö.'
    #                   }
    #             }
    #         ]}
    #     ],
    #     'slack': {},
    #     'billing': None,
    #     'billing_runners': None,
    #     'superuser': None,
    #     'github_username': None,
    #     'is_cph_user': None,
    #     'is_repo_owner': False,
    #     'captcha_token': None,
    #     '_id': ObjectId('6a3e967a2b4ccd43c982485a')
    # }

    assert u["email"] == "sso_user2@example.com"
    assert u["oauth_accounts"][0]["expires_at"] == exp
    # assert u["oauth_accounts"][0]["state"] == "active"
    # assert u["oauth_accounts"][0]["url"] == "https://test.example.com/orgs/test_gh_org"
    assert u["oauth_accounts"][0]["organizations"][0]["state"] == "active"
    # assert u["oauth_accounts"][0]["organizations"][0]["expires_at"] == exp
    assert (
        u["oauth_accounts"][0]["organizations"][0]["url"]
        == "https://test.example.com/orgs/test_gh_org"
    )
    assert (
        u["oauth_accounts"][0]["organizations"][0]["organization"]["login"]
        == "test_gh_org"
    )
    assert (
        u["oauth_accounts"][0]["organizations"][1]["url"]
        == "https://test.example.com/orgs/another_org"
    )
    assert (
        u["oauth_accounts"][0]["organizations"][1]["organization"]["login"]
        == "another_org"
    )

    # Update existing user
    # This one only refreshes the expires_at field
    exp += 11111
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
    assert (
        u["oauth_accounts"][0]["expires_at"] == exp
    ), "The existing oauth_account entry was refreshed"
    assert (
        u["oauth_accounts"][0]["organizations"][0]["url"]
        == "https://test.example.com/orgs/test_gh_org"
    )
    assert u["oauth_accounts"][0]["organizations"][0]["state"] == "active"
    assert (
        u["oauth_accounts"][0]["organizations"][0]["organization"]["login"]
        == "test_gh_org"
    )
    assert (
        u["oauth_accounts"][0]["organizations"][1]["url"]
        == "https://test.example.com/orgs/another_org"
    )
    assert (
        u["oauth_accounts"][0]["organizations"][1]["organization"]["login"]
        == "another_org"
    )

    # This should append new orgs in addition to pre-existing ones
    exp += 1
    fut = user_manager.oauth_callback(
        oauth_name="test.example.com",
        access_token="abcdef12345",
        account_id="255501024",
        account_email="sso_user@example.com",
        expires_at=exp,
        refresh_token="8ef8e5aa",
        associate_by_email=False,
    )
    user = asyncio.run(fut)
    print(vars(user))
    u = asyncio.run(store.get_user_without_any_fastapi_nonsense(user.id))
    print(u)
    assert u["email"] == "sso_user@example.com"
    assert (
        u["oauth_accounts"][0]["expires_at"] == exp
    ), "The existing oauth_account entry was refreshed"
    assert (
        u["oauth_accounts"][0]["organizations"][2]["url"]
        == "https://test.example.com/orgs/test_gh_org"
    )
    assert u["oauth_accounts"][0]["organizations"][2]["state"] == "active"
    assert (
        u["oauth_accounts"][0]["organizations"][2]["organization"]["login"]
        == "test_gh_org"
    )
    assert (
        u["oauth_accounts"][0]["organizations"][3]["url"]
        == "https://test.example.com/orgs/another_org"
    )
    assert (
        u["oauth_accounts"][0]["organizations"][3]["organization"]["login"]
        == "another_org"
    )

    # Now add a second openauth provider/source
    # Even if oauth_name makes this a unique and independent user,
    # For internal reasons we must reject users where account_id already exists,
    # even if it was from another provider completely
    with pytest.raises(UserAlreadyExists):
        exp += 1111
        fut = user_manager.oauth_callback(
            oauth_name="test2.example.com",
            access_token="345",
            account_id="255509999",
            account_email="sso_user2@example.com",
            expires_at=exp,
            refresh_token="8ef8e5aa",
            associate_by_email=False,
        )
        user = asyncio.run(fut)

    # Changing account_id and (optional) account_email and it works
    exp += 11
    fut = user_manager.oauth_callback(
        oauth_name="test2.example.com",
        access_token="345",
        account_id="255509999999",
        account_email="sso_user2222@example.com",
        expires_at=exp,
        refresh_token="8ef8e5aa",
        associate_by_email=False,
    )
    user = asyncio.run(fut)
    print(vars(user))
    u = asyncio.run(store.get_user_without_any_fastapi_nonsense(user.id))
    print(u)
    assert u["email"] == "sso_user2222@example.com"
    assert u["oauth_accounts"][0]["expires_at"] == exp
    assert (
        u["oauth_accounts"][0]["organizations"][0]["url"]
        == "https://test2.example.com/orgs/test_gh_org2"
    )
    assert u["oauth_accounts"][0]["organizations"][0]["state"] == "active"
    assert (
        u["oauth_accounts"][0]["organizations"][0]["organization"]["login"]
        == "test_gh_org2"
    )
