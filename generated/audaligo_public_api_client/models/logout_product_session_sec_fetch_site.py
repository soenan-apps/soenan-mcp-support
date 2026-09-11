from enum import StrEnum


class LogoutProductSessionSecFetchSite(StrEnum):
    SAME_ORIGIN = "same-origin"

    def __str__(self) -> str:
        return str(self.value)
