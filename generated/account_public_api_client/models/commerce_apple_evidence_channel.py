from enum import Enum


class CommerceAppleEvidenceChannel(str, Enum):
    APPLEAPPSTORE = "appleAppStore"

    def __str__(self) -> str:
        return str(self.value)
