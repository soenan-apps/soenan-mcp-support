from enum import Enum


class E2EeRealtimeEventType2Type(str, Enum):
    ROOT_REPLACEMENT = "root_replacement"

    def __str__(self) -> str:
        return str(self.value)
