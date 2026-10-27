from enum import Enum


class E2EeRootReplacementEventKind(str, Enum):
    ACCOUNT = "account"
    COMPLETE = "complete"
    DEVICE = "device"
    FRAGMENT = "fragment"
    HEADER = "header"
    ISSUER_EVIDENCE = "issuer_evidence"
    OWNER = "owner"
    RECOVERY = "recovery"
    SCOPE = "scope"

    def __str__(self) -> str:
        return str(self.value)
