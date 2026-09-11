from enum import StrEnum


class CreateChunkUploadCapabilitySecFetchSite(StrEnum):
    SAME_ORIGIN = "same-origin"

    def __str__(self) -> str:
        return str(self.value)
