from enum import IntEnum


class PreviewUploadMediaSampleRate(IntEnum):
    VALUE_48000 = 48000

    def __str__(self) -> str:
        return str(self.value)
