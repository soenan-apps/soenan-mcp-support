from enum import Enum


class CommercePurchaseCompletionRejectedCode(str, Enum):
    CANCELLED = "cancelled"
    FAILED = "failed"

    def __str__(self) -> str:
        return str(self.value)
