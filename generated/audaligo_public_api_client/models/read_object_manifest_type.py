from enum import StrEnum


class ReadObjectManifestType(StrEnum):
    AUDALIGO_MANAGED_ENCRYPTED_OBJECT_MANIFEST = (
        "audaligo.managed-encrypted-object-manifest"
    )

    def __str__(self) -> str:
        return str(self.value)
