from enum import Enum


class CommercePurchaseCompletionCheckoutReadyKind(str, Enum):
    CHECKOUTREADY = "checkoutReady"

    def __str__(self) -> str:
        return str(self.value)
