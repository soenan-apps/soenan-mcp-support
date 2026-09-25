from enum import Enum


class ReviewRectangleRegionKind(str, Enum):
    RECTANGLE = "rectangle"

    def __str__(self) -> str:
        return str(self.value)
