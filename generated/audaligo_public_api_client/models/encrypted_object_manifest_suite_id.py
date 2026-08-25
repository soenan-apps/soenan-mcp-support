from enum import Enum


class EncryptedObjectManifestSuiteId(str, Enum):
    AES_256_GCM_AUDALIGO_V1 = "aes-256-gcm-audaligo-v1"

    def __str__(self) -> str:
        return str(self.value)
