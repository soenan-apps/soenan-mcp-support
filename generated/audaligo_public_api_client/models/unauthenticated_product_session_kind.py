from enum import StrEnum


class UnauthenticatedProductSessionKind(StrEnum):
    UNAUTHENTICATED = "unauthenticated"

    def __str__(self) -> str:
        return str(self.value)
