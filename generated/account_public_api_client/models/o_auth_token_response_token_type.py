from enum import Enum


class OAuthTokenResponseTokenType(str, Enum):
    BEARER = "Bearer"

    def __str__(self) -> str:
        return str(self.value)
