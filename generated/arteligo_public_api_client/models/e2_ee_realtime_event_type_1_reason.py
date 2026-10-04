from enum import Enum


class E2EeRealtimeEventType1Reason(str, Enum):
    MEMBERSHIP_CHANGED = "membership_changed"
    RECONNECT = "reconnect"
    SUBSCRIBED = "subscribed"
    SUBSCRIBER_LAGGED = "subscriber_lagged"

    def __str__(self) -> str:
        return str(self.value)
