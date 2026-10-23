from enum import Enum


class E2EeInvitationParticipantProofKind(str, Enum):
    INVITATION = "invitation"

    def __str__(self) -> str:
        return str(self.value)
