from enum import StrEnum


class SwitchProductSessionOrganizationSecFetchSite(StrEnum):
    SAME_ORIGIN = "same-origin"

    def __str__(self) -> str:
        return str(self.value)
