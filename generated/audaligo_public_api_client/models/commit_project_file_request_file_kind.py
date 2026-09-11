from enum import StrEnum


class CommitProjectFileRequestFileKind(StrEnum):
    PROJECT_FILE = "project_file"

    def __str__(self) -> str:
        return str(self.value)
