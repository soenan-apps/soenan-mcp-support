from enum import Enum


class IdempotentMutationOutcome(str, Enum):
    APPLIED = "applied"
    IDEMPOTENT = "idempotent"

    def __str__(self) -> str:
        return str(self.value)
