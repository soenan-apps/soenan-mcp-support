from enum import Enum


class ReviewPinRegionKind(str, Enum):
    PIN = "pin"

    def __str__(self) -> str:
        return str(self.value)
