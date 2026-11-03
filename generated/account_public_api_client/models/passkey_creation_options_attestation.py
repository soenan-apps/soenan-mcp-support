from enum import Enum


class PasskeyCreationOptionsAttestation(str, Enum):
    NONE = "none"

    def __str__(self) -> str:
        return str(self.value)
