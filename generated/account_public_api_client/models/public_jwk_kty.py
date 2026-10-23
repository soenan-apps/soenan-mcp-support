from enum import Enum


class PublicJWKKty(str, Enum):
    RSA = "RSA"

    def __str__(self) -> str:
        return str(self.value)
