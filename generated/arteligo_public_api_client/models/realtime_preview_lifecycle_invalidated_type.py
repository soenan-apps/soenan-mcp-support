from enum import Enum


class RealtimePreviewLifecycleInvalidatedType(str, Enum):
    PREVIEW_LIFECYCLE_INVALIDATED = "preview_lifecycle_invalidated"

    def __str__(self) -> str:
        return str(self.value)
