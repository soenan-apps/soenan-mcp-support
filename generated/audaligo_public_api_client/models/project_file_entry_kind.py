from enum import StrEnum


class ProjectFileEntryKind(StrEnum):
    FILE = "file"

    def __str__(self) -> str:
        return str(self.value)
