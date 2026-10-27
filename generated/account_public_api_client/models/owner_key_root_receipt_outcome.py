from enum import Enum


class OwnerKeyRootReceiptOutcome(str, Enum):
    APPLIED = "applied"
    COVERED = "covered"

    def __str__(self) -> str:
        return str(self.value)
