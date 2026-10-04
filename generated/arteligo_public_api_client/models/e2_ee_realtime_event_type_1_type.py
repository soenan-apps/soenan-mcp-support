from enum import Enum


class E2EeRealtimeEventType1Type(str, Enum):
    CATCH_UP = "catch_up"

    def __str__(self) -> str:
        return str(self.value)
