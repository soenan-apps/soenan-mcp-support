from enum import Enum


class ChatEventType(str, Enum):
    DELETED = "deleted"
    EDITED = "edited"
    SENT = "sent"

    def __str__(self) -> str:
        return str(self.value)
