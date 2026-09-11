from enum import StrEnum


class ProjectParticipationPolicy(StrEnum):
    ORGANIZATION = "organization"
    PRIVATE = "private"

    def __str__(self) -> str:
        return str(self.value)
