from enum import Enum


class PreviewIntentMediaType(str, Enum):
    AUDIOWAV = "audio/wav"

    def __str__(self) -> str:
        return str(self.value)
