from enum import Enum


class CommerceManagementSessionKind(str, Enum):
    UNSUPPORTED = "unsupported"
    URL = "url"

    def __str__(self) -> str:
        return str(self.value)
