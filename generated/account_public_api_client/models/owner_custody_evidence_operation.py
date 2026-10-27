from enum import Enum


class OwnerCustodyEvidenceOperation(str, Enum):
    DEVICE_APPROVE = "device_approve"
    ENVELOPES_SAVE = "envelopes_save"
    RECOVERY_PUBLIC = "recovery_public"

    def __str__(self) -> str:
        return str(self.value)
