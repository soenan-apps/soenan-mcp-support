from enum import Enum


class E2EeRecipientKind(str, Enum):
    DEVICE = "device"
    ORGANIZATION = "organization"
    OWNER = "owner"
    RECOVERY = "recovery"

    def __str__(self) -> str:
        return str(self.value)
