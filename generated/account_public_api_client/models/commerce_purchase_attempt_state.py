from enum import Enum


class CommercePurchaseAttemptState(str, Enum):
    AWAITINGPROVIDER = "awaitingProvider"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    FAILED = "failed"
    PREPARED = "prepared"
    RECONCILIATIONPENDING = "reconciliationPending"
    VERIFYING = "verifying"

    def __str__(self) -> str:
        return str(self.value)
