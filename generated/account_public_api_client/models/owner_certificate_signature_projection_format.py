from enum import Enum


class OwnerCertificateSignatureProjectionFormat(str, Enum):
    SIGNATURE_PROJECTION_V1 = "signature_projection_v1"

    def __str__(self) -> str:
        return str(self.value)
