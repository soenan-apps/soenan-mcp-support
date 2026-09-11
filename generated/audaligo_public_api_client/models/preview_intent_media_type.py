from enum import StrEnum


class PreviewIntentMediaType(StrEnum):
    APPLICATIONOCTET_STREAM = "application/octet-stream"
    AUDIOWAV = "audio/wav"
    AUDIOWAVE = "audio/wave"
    AUDIOX_WAV = "audio/x-wav"
    VIDEOMP4 = "video/mp4"
    VIDEOQUICKTIME = "video/quicktime"
    VIDEOWEBM = "video/webm"

    def __str__(self) -> str:
        return str(self.value)
