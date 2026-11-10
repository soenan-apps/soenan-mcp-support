from enum import Enum


class CommercePurchaseCompletionAuthorizationEndedCode(str, Enum):
    EXPIRED = "expired"
    REVOKED = "revoked"

    def __str__(self) -> str:
        return str(self.value)
