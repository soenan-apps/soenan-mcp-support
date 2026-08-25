from enum import Enum


class PreviewObjectMimeType(str, Enum):
    AUDIOMP4 = "audio/mp4"

    def __str__(self) -> str:
        return str(self.value)
