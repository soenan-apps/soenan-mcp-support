from enum import Enum


class PutFilePreviewUploadManifestSecFetchSite(str, Enum):
    SAME_ORIGIN = "same-origin"

    def __str__(self) -> str:
        return str(self.value)
