from enum import Enum


class OrganizationCloseConflictError(str, Enum):
    ORGANIZATION_CLOSE_BLOCKED = "organization_close_blocked"

    def __str__(self) -> str:
        return str(self.value)
