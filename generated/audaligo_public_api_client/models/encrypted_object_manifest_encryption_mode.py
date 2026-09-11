from enum import StrEnum


class EncryptedObjectManifestEncryptionMode(StrEnum):
    MANAGED_PROJECT_KEY = "managed-project-key"

    def __str__(self) -> str:
        return str(self.value)
