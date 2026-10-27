from enum import Enum


class E2EeRootReplacementPendingEffectReason(str, Enum):
    AUTHORIZATION_CHANGED = "authorization_changed"
    SCOPE_CONFLICT = "scope_conflict"
    SUPERSEDED = "superseded"
    UNAVAILABLE = "unavailable"

    def __str__(self) -> str:
        return str(self.value)
