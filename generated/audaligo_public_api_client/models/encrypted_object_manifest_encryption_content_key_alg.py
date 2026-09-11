from enum import StrEnum


class EncryptedObjectManifestEncryptionContentKeyAlg(StrEnum):
    A256GCM = "A256GCM"

    def __str__(self) -> str:
        return str(self.value)
