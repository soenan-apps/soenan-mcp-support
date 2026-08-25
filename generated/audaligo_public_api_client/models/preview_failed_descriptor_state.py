from enum import Enum


class PreviewFailedDescriptorState(str, Enum):
    FAILED = "failed"

    def __str__(self) -> str:
        return str(self.value)
