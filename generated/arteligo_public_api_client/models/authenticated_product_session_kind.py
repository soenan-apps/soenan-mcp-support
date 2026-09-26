from enum import Enum


class AuthenticatedProductSessionKind(str, Enum):
    AUTHENTICATED = "authenticated"

    def __str__(self) -> str:
        return str(self.value)
