from enum import StrEnum


class InvitationSummaryAccessRole(StrEnum):
    EDITOR = "editor"
    VIEWER = "viewer"

    def __str__(self) -> str:
        return str(self.value)
