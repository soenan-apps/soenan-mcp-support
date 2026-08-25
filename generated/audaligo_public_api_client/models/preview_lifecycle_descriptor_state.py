from enum import Enum


class PreviewLifecycleDescriptorState(str, Enum):
    PROCESSING = "processing"
    WAITING = "waiting"

    def __str__(self) -> str:
        return str(self.value)
