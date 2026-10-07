from enum import Enum


class E2EeReadScopeResultError(str, Enum):
    ACCESS_DENIED = "access_denied"
    AUTHORIZATION_UNAVAILABLE = "authorization_unavailable"
    LIMIT_EXCEEDED = "limit_exceeded"
    NOT_FOUND = "not_found"

    def __str__(self) -> str:
        return str(self.value)
