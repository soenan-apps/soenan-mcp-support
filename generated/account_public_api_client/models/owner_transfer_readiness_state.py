from enum import Enum


class OwnerTransferReadinessState(str, Enum):
    BLOCKED = "blocked"
    READY = "ready"

    def __str__(self) -> str:
        return str(self.value)
