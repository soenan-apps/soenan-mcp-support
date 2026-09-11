from enum import StrEnum


class TermsAcceptanceRequiredProductSessionKind(StrEnum):
    TERMSACCEPTANCEREQUIRED = "termsAcceptanceRequired"

    def __str__(self) -> str:
        return str(self.value)
