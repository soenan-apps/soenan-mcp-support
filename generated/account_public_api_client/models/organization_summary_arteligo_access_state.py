from enum import Enum


class OrganizationSummaryArteligoAccessState(str, Enum):
    ORGANIZATION_INACTIVE = "organization_inactive"
    READY = "ready"
    ROLE_REQUIRED = "role_required"
    SEAT_REQUIRED = "seat_required"
    SUBSCRIPTION_REQUIRED = "subscription_required"

    def __str__(self) -> str:
        return str(self.value)
