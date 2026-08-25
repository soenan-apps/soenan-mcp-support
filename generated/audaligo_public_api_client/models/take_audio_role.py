from enum import Enum


class TakeAudioRole(str, Enum):
    MIX = "mix"
    VOICE = "voice"

    def __str__(self) -> str:
        return str(self.value)
