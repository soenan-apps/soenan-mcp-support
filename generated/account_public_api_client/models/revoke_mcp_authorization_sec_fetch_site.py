from enum import Enum


class RevokeMCPAuthorizationSecFetchSite(str, Enum):
    SAME_ORIGIN = "same-origin"

    def __str__(self) -> str:
        return str(self.value)
