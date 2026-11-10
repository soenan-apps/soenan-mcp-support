from enum import Enum


class CommercePurchaseCompletionWaitingKind(str, Enum):
    WAITING = "waiting"

    def __str__(self) -> str:
        return str(self.value)
