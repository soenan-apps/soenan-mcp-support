from enum import Enum


class PreviewUploadMediaCodecs(str, Enum):
    OPUS = "opus"

    def __str__(self) -> str:
        return str(self.value)
