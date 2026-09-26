from enum import Enum


class RealtimeErrorCode(str, Enum):
    AUTHORIZATION_EXPIRED = "authorization_expired"

    def __str__(self) -> str:
        return str(self.value)
