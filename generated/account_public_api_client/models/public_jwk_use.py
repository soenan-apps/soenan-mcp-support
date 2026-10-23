from enum import Enum


class PublicJWKUse(str, Enum):
    SIG = "sig"

    def __str__(self) -> str:
        return str(self.value)
