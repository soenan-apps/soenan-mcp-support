from enum import Enum


class ManualInvoiceContractInactiveReason(str, Enum):
    CONTRACTCONFLICT = "contractConflict"
    OWNERCLOSED = "ownerClosed"
    TERMENDED = "termEnded"

    def __str__(self) -> str:
        return str(self.value)
