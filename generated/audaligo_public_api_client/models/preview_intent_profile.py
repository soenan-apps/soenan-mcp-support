from enum import StrEnum


class PreviewIntentProfile(StrEnum):
    AAC_LC_128K_M4A_V1 = "aac-lc-128k-m4a-v1"
    H264_AAC_FMP4_V1 = "h264-aac-fmp4-v1"

    def __str__(self) -> str:
        return str(self.value)
