from enum import Enum


class RealtimeErrorType(str, Enum):
    REALTIME_ERROR = "realtime_error"

    def __str__(self) -> str:
        return str(self.value)
