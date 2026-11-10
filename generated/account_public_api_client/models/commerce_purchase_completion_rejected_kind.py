from enum import Enum


class CommercePurchaseCompletionRejectedKind(str, Enum):
    REJECTED = "rejected"

    def __str__(self) -> str:
        return str(self.value)
