from enum import Enum


class ProjectMemberAccessRole(str, Enum):
    EDITOR = "editor"
    OWNER = "owner"
    VIEWER = "viewer"

    def __str__(self) -> str:
        return str(self.value)
