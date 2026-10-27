from enum import Enum


class E2EeRootReplacementResultPhase(str, Enum):
    ACCOUNT_ACCEPTED = "account_accepted"
    ACCOUNT_PENDING = "account_pending"
    LOCALLY_APPLIED = "locally_applied"
    REJECTED = "rejected"

    def __str__(self) -> str:
        return str(self.value)
