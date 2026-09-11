from enum import StrEnum


class PreviewPlaybackLoudnessUnavailableKind(StrEnum):
    UNAVAILABLE = "unavailable"

    def __str__(self) -> str:
        return str(self.value)
