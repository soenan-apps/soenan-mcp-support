from enum import Enum


class ProjectListAccessSource(str, Enum):
    INVITATION = "invitation"
    ORGANIZATION = "organization"

    def __str__(self) -> str:
        return str(self.value)
