from enum import Enum


class OAuthAuthorizationServerMetadataGrantTypesSupportedItem(str, Enum):
    AUTHORIZATION_CODE = "authorization_code"
    REFRESH_TOKEN = "refresh_token"

    def __str__(self) -> str:
        return str(self.value)
