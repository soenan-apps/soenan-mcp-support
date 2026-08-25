from enum import Enum


class PreviewObjectCodec(str, Enum):
    MP4A_40_2 = "mp4a.40.2"

    def __str__(self) -> str:
        return str(self.value)
