from enum import StrEnum


class ChatEventType(StrEnum):
    DELETED = "deleted"
    EDITED = "edited"
    SENT = "sent"

    def __str__(self) -> str:
        return str(self.value)
