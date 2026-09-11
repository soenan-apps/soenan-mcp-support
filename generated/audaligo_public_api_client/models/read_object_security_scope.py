from enum import StrEnum


class ReadObjectSecurityScope(StrEnum):
    MANAGED_ENCRYPTION = "managed_encryption"
    MANAGED_PROCESSING = "managed_processing"

    def __str__(self) -> str:
        return str(self.value)
