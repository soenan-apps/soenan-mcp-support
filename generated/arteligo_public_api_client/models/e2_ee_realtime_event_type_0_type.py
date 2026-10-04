from enum import Enum


class E2EeRealtimeEventType0Type(str, Enum):
    RECORDS_CHANGED = "records_changed"

    def __str__(self) -> str:
        return str(self.value)
