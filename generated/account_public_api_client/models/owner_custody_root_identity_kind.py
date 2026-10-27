from enum import Enum


class OwnerCustodyRootIdentityKind(str, Enum):
    RECOVERY_ROOT = "recovery_root"

    def __str__(self) -> str:
        return str(self.value)
