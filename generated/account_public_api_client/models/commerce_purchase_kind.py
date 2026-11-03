from enum import Enum


class CommercePurchaseKind(str, Enum):
    PERPETUALLICENSE = "perpetualLicense"
    SUBSCRIPTION = "subscription"

    def __str__(self) -> str:
        return str(self.value)
