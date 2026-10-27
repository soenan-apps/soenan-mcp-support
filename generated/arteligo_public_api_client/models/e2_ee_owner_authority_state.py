from enum import Enum


class E2EeOwnerAuthorityState(str, Enum):
    ACTIVE = "active"
    ROTATION_REQUIRED = "rotation_required"
    UNPROVISIONED = "unprovisioned"

    def __str__(self) -> str:
        return str(self.value)
