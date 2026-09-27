from enum import Enum


class EncryptedProjectFileFileKind(str, Enum):
    PROJECT_FILE = "project_file"

    def __str__(self) -> str:
        return str(self.value)
