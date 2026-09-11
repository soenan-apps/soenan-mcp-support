from enum import StrEnum


class FileProjectReferenceKind(StrEnum):
    FILE = "file"

    def __str__(self) -> str:
        return str(self.value)
