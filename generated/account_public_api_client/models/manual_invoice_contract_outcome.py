from enum import Enum


class ManualInvoiceContractOutcome(str, Enum):
    ACTIVATED = "activated"
    PAYMENTINCOMPLETE = "paymentIncomplete"
    RECORDEDNOTACTIVATED = "recordedNotActivated"
    SCHEDULED = "scheduled"

    def __str__(self) -> str:
        return str(self.value)
