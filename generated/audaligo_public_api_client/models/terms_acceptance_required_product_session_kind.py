from enum import Enum


class TermsAcceptanceRequiredProductSessionKind(str, Enum):
    TERMSACCEPTANCEREQUIRED = "termsAcceptanceRequired"

    def __str__(self) -> str:
        return str(self.value)
