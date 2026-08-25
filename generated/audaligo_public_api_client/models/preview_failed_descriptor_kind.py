from enum import Enum


class PreviewFailedDescriptorKind(str, Enum):
    FAILED = "failed"

    def __str__(self) -> str:
        return str(self.value)
