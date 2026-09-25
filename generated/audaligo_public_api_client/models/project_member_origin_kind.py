from enum import Enum


class ProjectMemberOriginKind(str, Enum):
    INVITATION = "invitation"
    ORGANIZATION_PARTICIPATION = "organization_participation"
    PROJECT_CREATION = "project_creation"

    def __str__(self) -> str:
        return str(self.value)
