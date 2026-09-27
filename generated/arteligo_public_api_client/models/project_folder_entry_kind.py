from enum import Enum


class ProjectFolderEntryKind(str, Enum):
    FOLDER = "folder"

    def __str__(self) -> str:
        return str(self.value)
