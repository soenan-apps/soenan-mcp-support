from enum import StrEnum


class CreateInvitationRequestAccessRole(StrEnum):
    EDITOR = "editor"
    VIEWER = "viewer"

    def __str__(self) -> str:
        return str(self.value)
