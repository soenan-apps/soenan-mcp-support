from enum import StrEnum


class InvitationSummaryState(StrEnum):
    PENDING = "pending"

    def __str__(self) -> str:
        return str(self.value)
