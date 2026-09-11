from enum import StrEnum


class ProjectFileSourceState(StrEnum):
    AVAILABLE = "available"
    DELETED = "deleted"

    def __str__(self) -> str:
        return str(self.value)
