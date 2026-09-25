from enum import Enum


class PreviewPlaybackLoudnessMeasuredKind(str, Enum):
    MEASURED = "measured"

    def __str__(self) -> str:
        return str(self.value)
