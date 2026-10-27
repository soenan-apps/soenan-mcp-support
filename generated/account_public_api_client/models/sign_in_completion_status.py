from enum import Enum


class SignInCompletionStatus(str, Enum):
    AUTHENTICATED = "authenticated"

    def __str__(self) -> str:
        return str(self.value)
