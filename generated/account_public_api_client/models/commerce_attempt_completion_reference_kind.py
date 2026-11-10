from enum import Enum


class CommerceAttemptCompletionReferenceKind(str, Enum):
    ATTEMPT = "attempt"

    def __str__(self) -> str:
        return str(self.value)
