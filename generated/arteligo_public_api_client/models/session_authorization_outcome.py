from enum import Enum

class SessionAuthorizationOutcome(str, Enum):
    EXPIRED = "expired"
    PENDING = "pending"
    READY = "ready"

    def __str__(self) -> str:
        return str(self.value)
