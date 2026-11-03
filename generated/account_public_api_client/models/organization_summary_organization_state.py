from enum import Enum


class OrganizationSummaryOrganizationState(str, Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    SUSPENDED = "suspended"

    def __str__(self) -> str:
        return str(self.value)
