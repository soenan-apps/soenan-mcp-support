from enum import Enum


class EncryptedObjectManifestEncryptionWrapAlg(str, Enum):
    A256GCM_PROJECT_EPOCH_V1 = "a256gcm-project-epoch-v1"

    def __str__(self) -> str:
        return str(self.value)
