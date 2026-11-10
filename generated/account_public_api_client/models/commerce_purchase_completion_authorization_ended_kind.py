from enum import Enum


class CommercePurchaseCompletionAuthorizationEndedKind(str, Enum):
    AUTHORIZATIONENDED = "authorizationEnded"

    def __str__(self) -> str:
        return str(self.value)
