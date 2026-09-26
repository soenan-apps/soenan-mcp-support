from enum import IntEnum


class PreviewUploadManifestChunkSize(IntEnum):
    VALUE_8388608 = 8388608

    def __str__(self) -> str:
        return str(self.value)
