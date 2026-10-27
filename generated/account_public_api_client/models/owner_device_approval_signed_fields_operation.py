from enum import Enum


class OwnerDeviceApprovalSignedFieldsOperation(str, Enum):
    DEVICE_APPROVE = "device_approve"

    def __str__(self) -> str:
        return str(self.value)
