from enum import Enum


class CommerceGoogleEvidenceChannel(str, Enum):
    GOOGLEPLAYSTORE = "googlePlayStore"

    def __str__(self) -> str:
        return str(self.value)
