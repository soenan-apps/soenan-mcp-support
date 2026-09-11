from enum import StrEnum


class FileReviewAnchorKind(StrEnum):
    FILE = "file"

    def __str__(self) -> str:
        return str(self.value)
