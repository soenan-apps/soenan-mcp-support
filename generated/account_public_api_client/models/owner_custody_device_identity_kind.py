from enum import Enum


class OwnerCustodyDeviceIdentityKind(str, Enum):
    DEVICE = "device"

    def __str__(self) -> str:
        return str(self.value)
