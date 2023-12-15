# Copyright (c) 2024, Nyrkiö Oy

from typing import Union
from pydantic import BaseModel

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # noqa: E501
        "disabled": False,
        "is_admin": False,
    }
}


class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None
    is_admin: Union[bool, None] = None


class UserInDB(User):
    hashed_password: str


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


class DBStore(object):
    """
    A simple in-memory database for storing users.

    This is a singleton class, so there can only be one instance of it.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DBStore, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.db = fake_users_db

    def add_user(self, user: User):
        # We rely on GitHub OAuth to provide us with a unique username
        self.db[user.username] = user
