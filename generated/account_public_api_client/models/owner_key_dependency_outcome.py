from enum import Enum


class OwnerKeyDependencyOutcome(str, Enum):
    AVAILABLE = "available"
    DENIED = "denied"
    MISSING = "missing"

    def __str__(self) -> str:
        return str(self.value)
