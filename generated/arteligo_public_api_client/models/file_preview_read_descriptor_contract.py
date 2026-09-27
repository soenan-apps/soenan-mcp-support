from enum import Enum


class FilePreviewReadDescriptorContract(str, Enum):
    AUDALIGO_PREVIEW_READ_V1 = "audaligo.preview.read.v1"

    def __str__(self) -> str:
        return str(self.value)
