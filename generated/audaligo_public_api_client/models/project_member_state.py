from enum import StrEnum


class ProjectMemberState(StrEnum):
    ACTIVE = "active"
    REMOVED = "removed"

    def __str__(self) -> str:
        return str(self.value)
