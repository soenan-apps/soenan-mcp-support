from enum import Enum


class ProjectFileEntryKind(str, Enum):
    FILE = "file"

    def __str__(self) -> str:
        return str(self.value)
