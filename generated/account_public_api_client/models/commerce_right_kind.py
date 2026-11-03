from enum import Enum


class CommerceRightKind(str, Enum):
    ARTELIGOGROUPCAPACITY = "arteligoGroupCapacity"
    PERPETUALLICENSE = "perpetualLicense"
    SUBSCRIPTION = "subscription"

    def __str__(self) -> str:
        return str(self.value)
