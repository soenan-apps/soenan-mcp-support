from enum import StrEnum


class AuthenticatedProductSessionKind(StrEnum):
    AUTHENTICATED = "authenticated"

    def __str__(self) -> str:
        return str(self.value)
