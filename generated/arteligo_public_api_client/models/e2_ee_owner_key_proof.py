from enum import Enum


class E2EeOwnerKeyProof(str, Enum):
    HPKE_AUTH_V1 = "hpke_auth_v1"

    def __str__(self) -> str:
        return str(self.value)
