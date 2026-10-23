from enum import Enum


class EmailSubmission(str, Enum):
    ACCEPTED = "accepted"
    UNKNOWN = "unknown"

    def __str__(self) -> str:
        return str(self.value)
