from enum import StrEnum


class ProjectMemberOriginKind(StrEnum):
    INVITATION = "invitation"
    ORGANIZATION_PARTICIPATION = "organization_participation"
    PROJECT_CREATION = "project_creation"

    def __str__(self) -> str:
        return str(self.value)
