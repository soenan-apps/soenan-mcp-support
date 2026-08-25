from enum import Enum


class InvitationSummaryState(str, Enum):
    PENDING = "pending"

    def __str__(self) -> str:
        return str(self.value)
