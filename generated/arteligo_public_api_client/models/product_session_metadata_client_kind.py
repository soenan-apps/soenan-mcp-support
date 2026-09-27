from enum import Enum


class ProductSessionMetadataClientKind(str, Enum):
    NATIVE = "native"
    WEB = "web"

    def __str__(self) -> str:
        return str(self.value)
