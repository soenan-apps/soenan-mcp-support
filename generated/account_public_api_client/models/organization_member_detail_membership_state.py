from enum import Enum


class OrganizationMemberDetailMembershipState(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"

    def __str__(self) -> str:
        return str(self.value)
