from enum import StrEnum


class FilePreviewStateState(StrEnum):
    FAILED = "failed"
    PROCESSING = "processing"
    QUEUED = "queued"
    READY = "ready"

    def __str__(self) -> str:
        return str(self.value)
