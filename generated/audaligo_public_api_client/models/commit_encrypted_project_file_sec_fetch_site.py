from enum import StrEnum


class CommitEncryptedProjectFileSecFetchSite(StrEnum):
    SAME_ORIGIN = "same-origin"

    def __str__(self) -> str:
        return str(self.value)
