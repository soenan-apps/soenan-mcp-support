from enum import Enum


class UnauthenticatedProductSessionKind(str, Enum):
    UNAUTHENTICATED = "unauthenticated"

    def __str__(self) -> str:
        return str(self.value)
