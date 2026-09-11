from enum import StrEnum


class ReviewPinRegionKind(StrEnum):
    PIN = "pin"

    def __str__(self) -> str:
        return str(self.value)
