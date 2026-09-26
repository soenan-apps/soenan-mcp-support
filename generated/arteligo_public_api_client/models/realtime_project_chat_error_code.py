from enum import Enum


class RealtimeProjectChatErrorCode(str, Enum):
    ACCESS_DENIED = "access_denied"
    INVALID_REQUEST = "invalid_request"
    RATE_LIMITED = "rate_limited"
    SERVICE_UNAVAILABLE = "service_unavailable"

    def __str__(self) -> str:
        return str(self.value)
