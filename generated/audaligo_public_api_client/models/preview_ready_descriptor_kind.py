from enum import Enum


class PreviewReadyDescriptorKind(str, Enum):
    READY = "ready"

    def __str__(self) -> str:
        return str(self.value)
