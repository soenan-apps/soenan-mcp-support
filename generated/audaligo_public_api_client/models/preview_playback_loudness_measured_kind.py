from enum import StrEnum


class PreviewPlaybackLoudnessMeasuredKind(StrEnum):
    MEASURED = "measured"

    def __str__(self) -> str:
        return str(self.value)
