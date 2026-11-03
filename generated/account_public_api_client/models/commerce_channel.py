from enum import Enum


class CommerceChannel(str, Enum):
    APPLEAPPSTORE = "appleAppStore"
    GOOGLEPLAYSTORE = "googlePlayStore"
    SOENANSTORE = "soenanStore"

    def __str__(self) -> str:
        return str(self.value)
