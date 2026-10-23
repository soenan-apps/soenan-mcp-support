from enum import Enum


class CommerceRightState(str, Enum):
    EFFECTIVE = "effective"
    ENDED = "ended"
    PENDING = "pending"
    REVOKED = "revoked"
    SUSPENDED = "suspended"

    def __str__(self) -> str:
        return str(self.value)
