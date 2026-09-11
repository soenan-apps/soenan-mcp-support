from enum import StrEnum


class UpdateProjectTaskSecFetchSite(StrEnum):
    SAME_ORIGIN = "same-origin"

    def __str__(self) -> str:
        return str(self.value)
