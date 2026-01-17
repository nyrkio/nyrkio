import os
from typing import Optional, List, Any, Tuple, Dict

from httpx_oauth.clients.openid import OpenID
from httpx_oauth.exceptions import GetIdEmailError

CLIENT_ID = os.environ.get("ONE_LOGIN_CLIENT_ID", None)
CLIENT_SECRET = os.environ.get("ONE_LOGIN_CLIENT_SECRET", None)
ONELOGIN_REDIRECT_URI = "https://staging.nyrkio.com/api/v0/auth/onelogin/mycallback"
ONELOGIN_OIDC_HOST = "openid-connect.onelogin.com"

BASE_SCOPES = ["openid", "profile", "groups"]


class OneLoginOAuth2(OpenID):
    """OAuth2 client for OneLogin."""

    def __init__(
        self,
        sso_domain: str,
        scopes: Optional[List[str]] = BASE_SCOPES,
        name: str = "onelogin",
    ):
        """
        Args:
            client_id: The client ID provided by the OAuth2 provider.
            client_secret: The client secret provided by the OAuth2 provider.
            okta_domain: The Okta organization domain.
            scopes: The default scopes to be used in the authorization URL.
            name: A unique name for the OAuth2 client.
        """
        self.userinfo = None  # None means we didn't even try to get it yet.

        super().__init__(
            CLIENT_ID,
            CLIENT_SECRET,
            f"https://{sso_domain}/oidc/2/.well-known/openid-configuration",
            name=name,
            base_scopes=scopes,
        )
        print(self.openid_configuration)

    # Override so we can get more of the data than just an email
    async def get_id_email(self, token: str) -> Tuple[str, Optional[str]]:
        async with self.get_httpx_client() as client:
            response = await client.get(
                self.openid_configuration["userinfo_endpoint"],
                headers={**self.request_headers, "Authorization": f"Bearer {token}"},
            )

            if response.status_code >= 400:
                raise GetIdEmailError(response.json())

            self.userinfo: Dict[str, Any] = response.json()

            return str(self.userinfo["sub"]), self.userinfo.get("email")

    async def get_userinfo(self, token: str) -> Dict[str, Any]:
        if self.userinfo is None:
            await self.get_id_email(token)
        return self.userinfo
