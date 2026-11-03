from enum import Enum


class SessionAuthorizationOutcome(str, Enum):
    DELIVERY_PENDING = "delivery_pending"
    DENIED = "denied"
    EXPIRED = "expired"
    READY = "ready"
    SOURCE_BEHIND = "source_behind"

    def __str__(self) -> str:
        return str(self.value)
