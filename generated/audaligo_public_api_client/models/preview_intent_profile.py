from enum import Enum


class PreviewIntentProfile(str, Enum):
    AAC_LC_128K_M4A_V1 = "aac-lc-128k-m4a-v1"
    H264_AAC_FMP4_V1 = "h264-aac-fmp4-v1"
    OPUS_WEBM_V1 = "opus-webm-v1"

    def __str__(self) -> str:
        return str(self.value)
