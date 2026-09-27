from enum import Enum


class ProjectFileSourceState(str, Enum):
    AVAILABLE = "available"
    DELETED = "deleted"

    def __str__(self) -> str:
        return str(self.value)
