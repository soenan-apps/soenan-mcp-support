from enum import Enum


class CommercePurchaseCompletionConfirmedKind(str, Enum):
    CONFIRMED = "confirmed"

    def __str__(self) -> str:
        return str(self.value)
