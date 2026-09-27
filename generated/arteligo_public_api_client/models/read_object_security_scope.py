from enum import Enum


class ReadObjectSecurityScope(str, Enum):
    MANAGED_ENCRYPTION = "managed_encryption"
    MANAGED_PROCESSING = "managed_processing"

    def __str__(self) -> str:
        return str(self.value)
