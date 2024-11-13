from typing import Optional

from fastapi_users import BaseUserManager, models, exceptions
from fastapi_users.authentication.strategy import JWTStrategy


# Originally stored in Mongodb, but this is quite a frequent call
# FIXME: Will break on multiple backend nodes
superuser_active_map = {}


class SuperuserStrategy(JWTStrategy):
    def __init__(
        self,
        lifetime_seconds: Optional[int],
        secret: str = "qwerty",
    ):
        super().__init__(lifetime_seconds=lifetime_seconds, secret=secret)

    async def read_token(
        self, token: Optional[str], user_manager: BaseUserManager[models.UP, models.ID]
    ) -> Optional[models.UP]:
        admin_user = await super().read_token(token, user_manager)
        if admin_user is None:
            return None

        if not admin_user.is_superuser:
            return admin_user

        user = superuser_active_map.get(admin_user.email)
        if not user:
            return admin_user
        try:
            impersonate_user = await user_manager.get(user.id)
            impersonate_user.superuser = {"user_email": admin_user.email}
            return impersonate_user
        except exceptions.InvalidID:
            print("superuser: InvalidID")
            return admin_user
        except exceptions.UserNotExists:
            print("superuser: UserNotExists")
            return admin_user

    async def destroy_token(self, admin_user: str, user: models.UP) -> None:
        # await self.store.delete_impersonate_user(token)
        del superuser_active_map[admin_user]
