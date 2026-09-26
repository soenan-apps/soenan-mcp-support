from enum import Enum


class PreviewUploadLoudnessMeasuredKind(str, Enum):
    MEASURED = "measured"

    def __str__(self) -> str:
        return str(self.value)
