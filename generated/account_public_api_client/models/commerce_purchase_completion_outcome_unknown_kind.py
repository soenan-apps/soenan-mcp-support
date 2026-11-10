from enum import Enum


class CommercePurchaseCompletionOutcomeUnknownKind(str, Enum):
    OUTCOMEUNKNOWN = "outcomeUnknown"

    def __str__(self) -> str:
        return str(self.value)
