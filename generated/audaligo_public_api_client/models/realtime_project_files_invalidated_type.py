from enum import Enum


class RealtimeProjectFilesInvalidatedType(str, Enum):
    PROJECT_FILES_INVALIDATED = "project_files_invalidated"

    def __str__(self) -> str:
        return str(self.value)
