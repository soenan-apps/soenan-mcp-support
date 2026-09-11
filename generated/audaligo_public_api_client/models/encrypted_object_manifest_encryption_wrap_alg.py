from enum import StrEnum


class EncryptedObjectManifestEncryptionWrapAlg(StrEnum):
    A256GCM_PROJECT_EPOCH_V1 = "a256gcm-project-epoch-v1"

    def __str__(self) -> str:
        return str(self.value)
