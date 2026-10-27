from enum import Enum


class OwnerKeyReferenceKind(str, Enum):
    CERTIFICATE_PROJECTION = "certificate_projection"
    CUSTODY_EVIDENCE = "custody_evidence"
    CUSTODY_RECEIPT = "custody_receipt"
    SELECTED_BINDING = "selected_binding"
    TRANSFER_DECISION = "transfer_decision"

    def __str__(self) -> str:
        return str(self.value)
