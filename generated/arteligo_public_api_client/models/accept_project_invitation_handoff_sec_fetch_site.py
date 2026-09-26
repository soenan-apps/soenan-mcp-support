from enum import Enum


class AcceptProjectInvitationHandoffSecFetchSite(str, Enum):
    SAME_ORIGIN = "same-origin"

    def __str__(self) -> str:
        return str(self.value)
