from enum import Enum


class SignUpCompletionStatus(str, Enum):
    REGISTERED = "registered"

    def __str__(self) -> str:
        return str(self.value)
