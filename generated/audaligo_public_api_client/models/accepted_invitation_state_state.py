from enum import Enum


class AcceptedInvitationStateState(str, Enum):
    ACCEPTED = "accepted"

    def __str__(self) -> str:
        return str(self.value)
