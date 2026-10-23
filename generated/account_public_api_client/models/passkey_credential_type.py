from enum import Enum


class PasskeyCredentialType(str, Enum):
    PUBLIC_KEY = "public-key"

    def __str__(self) -> str:
        return str(self.value)
