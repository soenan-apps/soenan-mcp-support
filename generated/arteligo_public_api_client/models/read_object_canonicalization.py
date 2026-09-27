from enum import Enum


class ReadObjectCanonicalization(str, Enum):
    JCS_RFC8785 = "JCS-RFC8785"

    def __str__(self) -> str:
        return str(self.value)
