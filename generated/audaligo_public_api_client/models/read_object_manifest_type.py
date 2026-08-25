from enum import Enum


class ReadObjectManifestType(str, Enum):
    AUDALIGO_MANAGED_ENCRYPTED_OBJECT_MANIFEST = "audaligo.managed-encrypted-object-manifest"

    def __str__(self) -> str:
        return str(self.value)
