from enum import Enum


class OrganizationSummaryMembershipState(str, Enum):
    ACTIVE = "active"
    REMOVED = "removed"
    SUSPENDED = "suspended"

    def __str__(self) -> str:
        return str(self.value)
