from enum import Enum


class OwnerTransferResultEmailDeliveryState(str, Enum):
    ACCEPTED = "accepted"
    NOT_REQUIRED = "not_required"
    PENDING = "pending"

    def __str__(self) -> str:
        return str(self.value)
