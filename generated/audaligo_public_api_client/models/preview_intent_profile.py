from enum import Enum


class PreviewIntentProfile(str, Enum):
    AAC_LC_128K_M4A_V1 = "aac-lc-128k-m4a-v1"

    def __str__(self) -> str:
        return str(self.value)
