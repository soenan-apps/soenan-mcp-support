from enum import Enum


class OAuthClientRegistrationRequestTokenEndpointAuthMethod(str, Enum):
    NONE = "none"

    def __str__(self) -> str:
        return str(self.value)
