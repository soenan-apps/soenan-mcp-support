from enum import Enum


class PreviewLifecycleDescriptorKind(str, Enum):
    LIFECYCLE = "lifecycle"

    def __str__(self) -> str:
        return str(self.value)
