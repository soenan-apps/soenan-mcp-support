from enum import Enum


class PasskeyAuthenticationCompletionStatus(str, Enum):
    AUTHENTICATED = "authenticated"

    def __str__(self) -> str:
        return str(self.value)
