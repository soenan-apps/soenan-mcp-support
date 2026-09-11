from enum import StrEnum


class ProductSessionMetadataClientKind(StrEnum):
    WEB = "web"

    def __str__(self) -> str:
        return str(self.value)
