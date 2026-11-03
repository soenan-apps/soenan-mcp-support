from enum import Enum


class OrganizationCloseSimpleBlockerKind(str, Enum):
    CHECKOUT_PENDING = "checkout_pending"
    SUBSCRIPTION_ACTIVE = "subscription_active"

    def __str__(self) -> str:
        return str(self.value)
