from enum import Enum


class PreviewUploadSessionState(str, Enum):
    READY = "ready"
    RESERVED = "reserved"
    WAITING = "waiting"

    def __str__(self) -> str:
        return str(self.value)
