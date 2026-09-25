from enum import Enum


class RealtimeProjectChangesCatchUpRequiredReason(str, Enum):
    AUTHORIZATION_CHANGED = "authorization_changed"
    FANOUT_UNAVAILABLE = "fanout_unavailable"
    REVISION_EXHAUSTED = "revision_exhausted"
    SUBSCRIBER_LAGGED = "subscriber_lagged"

    def __str__(self) -> str:
        return str(self.value)
