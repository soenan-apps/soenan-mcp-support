from enum import StrEnum


class CurrentMembershipAccessRole(StrEnum):
    EDITOR = "editor"
    OWNER = "owner"
    VIEWER = "viewer"

    def __str__(self) -> str:
        return str(self.value)
