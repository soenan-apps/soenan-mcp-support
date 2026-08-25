from enum import Enum


class InvitationMembershipAccessRole(str, Enum):
    EDITOR = "editor"
    OWNER = "owner"

    def __str__(self) -> str:
        return str(self.value)
