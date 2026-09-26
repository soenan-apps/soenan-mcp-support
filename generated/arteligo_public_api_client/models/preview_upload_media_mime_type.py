from enum import Enum


class PreviewUploadMediaMimeType(str, Enum):
    AUDIOWEBM = "audio/webm"

    def __str__(self) -> str:
        return str(self.value)
