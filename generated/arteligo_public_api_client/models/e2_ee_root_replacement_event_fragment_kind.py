from enum import Enum


class E2EeRootReplacementEventFragmentKind(str, Enum):
    ACCOUNT = "account"
    DEVICE = "device"
    HEADER = "header"
    ISSUER_EVIDENCE = "issuer_evidence"
    OWNER = "owner"
    RECOVERY = "recovery"
    SCOPE = "scope"

    def __str__(self) -> str:
        return str(self.value)
