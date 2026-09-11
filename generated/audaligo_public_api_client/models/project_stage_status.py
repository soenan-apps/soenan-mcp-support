from enum import StrEnum


class ProjectStageStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"

    def __str__(self) -> str:
        return str(self.value)
