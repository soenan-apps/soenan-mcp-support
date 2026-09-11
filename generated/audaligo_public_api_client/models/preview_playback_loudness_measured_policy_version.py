from enum import StrEnum


class PreviewPlaybackLoudnessMeasuredPolicyVersion(StrEnum):
    EBU_R128_PLAYBACK_V1 = "ebu-r128-playback-v1"

    def __str__(self) -> str:
        return str(self.value)
