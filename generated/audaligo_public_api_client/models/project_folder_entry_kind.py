from enum import StrEnum


class ProjectFolderEntryKind(StrEnum):
    FOLDER = "folder"

    def __str__(self) -> str:
        return str(self.value)
