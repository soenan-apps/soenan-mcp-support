from enum import Enum


class ProductSessionMetadataClientKind(str, Enum):
    WEB = "web"

    def __str__(self) -> str:
        return str(self.value)
