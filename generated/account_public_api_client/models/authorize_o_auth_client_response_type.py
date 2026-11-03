from enum import Enum


class AuthorizeOAuthClientResponseType(str, Enum):
    CODE = "code"

    def __str__(self) -> str:
        return str(self.value)
