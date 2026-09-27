from enum import Enum


class InvitationStateAccessRole(str, Enum):
    EDITOR = "editor"
    VIEWER = "viewer"

    def __str__(self) -> str:
        return str(self.value)
