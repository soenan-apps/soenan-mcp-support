from enum import Enum


class PreviewPlaybackLoudnessUnmeasurableKind(str, Enum):
    UNMEASURABLE = "unmeasurable"

    def __str__(self) -> str:
        return str(self.value)
