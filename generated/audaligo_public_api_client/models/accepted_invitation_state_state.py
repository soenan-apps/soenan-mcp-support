from enum import StrEnum


class AcceptedInvitationStateState(StrEnum):
    ACCEPTED = "accepted"

    def __str__(self) -> str:
        return str(self.value)
