from enum import Enum


class OAuthAuthorizationServerMetadataResponseTypesSupportedItem(str, Enum):
    CODE = "code"

    def __str__(self) -> str:
        return str(self.value)
