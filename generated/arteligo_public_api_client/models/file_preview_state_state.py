from enum import Enum


class FilePreviewStateState(str, Enum):
    FAILED = "failed"
    PROCESSING = "processing"
    QUEUED = "queued"
    READY = "ready"

    def __str__(self) -> str:
        return str(self.value)
