from enum import Enum


class E2EeOwnerTransferDecisionState(str, Enum):
    ABORTED = "aborted"
    COMMITTED = "committed"
    PENDING = "pending"

    def __str__(self) -> str:
        return str(self.value)
