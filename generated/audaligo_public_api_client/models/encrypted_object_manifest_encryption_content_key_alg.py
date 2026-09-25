from enum import Enum


class EncryptedObjectManifestEncryptionContentKeyAlg(str, Enum):
    A256GCM = "A256GCM"

    def __str__(self) -> str:
        return str(self.value)
