from enum import Enum


class OrganizationInvitationDetailState(str, Enum):
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    PENDING = "pending"
    REVOKED = "revoked"

    def __str__(self) -> str:
        return str(self.value)
