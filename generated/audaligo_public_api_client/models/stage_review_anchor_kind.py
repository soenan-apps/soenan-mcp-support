from enum import StrEnum


class StageReviewAnchorKind(StrEnum):
    STAGE = "stage"

    def __str__(self) -> str:
        return str(self.value)
