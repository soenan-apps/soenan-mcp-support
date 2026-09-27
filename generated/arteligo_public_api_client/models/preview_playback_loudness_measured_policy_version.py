from enum import Enum


class PreviewPlaybackLoudnessMeasuredPolicyVersion(str, Enum):
    EBU_R128_PLAYBACK_V1 = "ebu-r128-playback-v1"

    def __str__(self) -> str:
        return str(self.value)
