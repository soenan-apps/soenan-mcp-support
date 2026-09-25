from enum import Enum


class CommitProjectFileRequestFileKind(str, Enum):
    PROJECT_FILE = "project_file"

    def __str__(self) -> str:
        return str(self.value)
