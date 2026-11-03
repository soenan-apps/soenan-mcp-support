from enum import Enum


class CommerceProviderStartKind(str, Enum):
    HOSTEDSESSION = "hostedSession"
    NATIVEPURCHASE = "nativePurchase"
    OUTCOMEUNKNOWN = "outcomeUnknown"
    UNSUPPORTED = "unsupported"

    def __str__(self) -> str:
        return str(self.value)
