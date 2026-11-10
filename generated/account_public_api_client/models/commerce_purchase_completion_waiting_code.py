from enum import Enum


class CommercePurchaseCompletionWaitingCode(str, Enum):
    PROCESSING = "processing"
    PROVIDERPENDING = "providerPending"

    def __str__(self) -> str:
        return str(self.value)
