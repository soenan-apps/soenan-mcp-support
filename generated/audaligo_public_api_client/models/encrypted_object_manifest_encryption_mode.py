from enum import Enum


class EncryptedObjectManifestEncryptionMode(str, Enum):
    MANAGED_PROJECT_KEY = "managed-project-key"

    def __str__(self) -> str:
        return str(self.value)
