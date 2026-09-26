from enum import Enum


class RealtimeProjectChatCatchUpRequiredReason(str, Enum):
    AUTHORIZATION_CHANGED = "authorization_changed"
    CURSOR_GAP = "cursor_gap"
    FANOUT_UNAVAILABLE = "fanout_unavailable"
    SUBSCRIBER_LAGGED = "subscriber_lagged"

    def __str__(self) -> str:
        return str(self.value)
