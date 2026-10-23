from enum import Enum


class E2EeOrganizationParticipantProofKind(str, Enum):
    ORGANIZATION = "organization"

    def __str__(self) -> str:
        return str(self.value)
