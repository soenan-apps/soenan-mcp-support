from enum import StrEnum


class EncryptedProjectFileFileKind(StrEnum):
    PROJECT_FILE = "project_file"

    def __str__(self) -> str:
        return str(self.value)
