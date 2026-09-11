from enum import StrEnum


class DeleteProjectChatMessageSecFetchSite(StrEnum):
    SAME_ORIGIN = "same-origin"

    def __str__(self) -> str:
        return str(self.value)
