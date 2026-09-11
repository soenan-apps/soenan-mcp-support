from enum import StrEnum


class ReadObjectCanonicalization(StrEnum):
    JCS_RFC8785 = "JCS-RFC8785"

    def __str__(self) -> str:
        return str(self.value)
