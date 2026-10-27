from enum import Enum


class OwnerKeyOperationRejectionReason(str, Enum):
    ACCESS_DENIED = "access_denied"
    CONFLICT = "conflict"
    INVALID_REQUEST = "invalid_request"
    PREPARATION_EXPIRED = "preparation_expired"
    STATE_CHANGED = "state_changed"

    def __str__(self) -> str:
        return str(self.value)
