from enum import Enum


class OwnerTransferResultState(str, Enum):
    BLOCKED = "blocked"
    COMPLETED = "completed"
    PENDING = "pending"

    def __str__(self) -> str:
        return str(self.value)
