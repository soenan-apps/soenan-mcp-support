from enum import Enum


class CommercePurchaseCompletionOutcomeUnknownCode(str, Enum):
    COMMITUNKNOWN = "commitUnknown"

    def __str__(self) -> str:
        return str(self.value)
