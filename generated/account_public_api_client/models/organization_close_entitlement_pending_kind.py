from enum import Enum


class OrganizationCloseEntitlementPendingKind(str, Enum):
    ENTITLEMENT_PENDING = "entitlement_pending"

    def __str__(self) -> str:
        return str(self.value)
