from enum import Enum


class E2EeRecipientPurpose(str, Enum):
    ADMISSION = "admission"
    DISTRIBUTION = "distribution"

    def __str__(self) -> str:
        return str(self.value)
