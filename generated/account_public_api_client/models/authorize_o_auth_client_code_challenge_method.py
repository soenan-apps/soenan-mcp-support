from enum import Enum


class AuthorizeOAuthClientCodeChallengeMethod(str, Enum):
    S256 = "S256"

    def __str__(self) -> str:
        return str(self.value)
