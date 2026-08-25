from enum import Enum


class PreviewReadDescriptorContract(str, Enum):
    AUDALIGO_MANAGED_PREVIEW_READ_DESCRIPTOR = "audaligo.managed-preview-read-descriptor"

    def __str__(self) -> str:
        return str(self.value)
