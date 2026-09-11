from enum import StrEnum


class InvitationStateState(StrEnum):
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    PENDING = "pending"
    REVOKED = "revoked"

    def __str__(self) -> str:
        return str(self.value)
