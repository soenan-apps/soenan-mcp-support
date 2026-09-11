from enum import StrEnum


class PreviewPlaybackLoudnessUnmeasurableKind(StrEnum):
    UNMEASURABLE = "unmeasurable"

    def __str__(self) -> str:
        return str(self.value)
