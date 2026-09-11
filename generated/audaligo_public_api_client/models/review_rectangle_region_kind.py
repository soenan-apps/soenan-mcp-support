from enum import StrEnum


class ReviewRectangleRegionKind(StrEnum):
    RECTANGLE = "rectangle"

    def __str__(self) -> str:
        return str(self.value)
