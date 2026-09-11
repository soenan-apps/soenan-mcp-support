from enum import StrEnum


class ProjectListAccessSource(StrEnum):
    INVITATION = "invitation"
    ORGANIZATION = "organization"

    def __str__(self) -> str:
        return str(self.value)
