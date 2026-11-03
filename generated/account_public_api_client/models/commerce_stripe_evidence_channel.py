from enum import Enum


class CommerceStripeEvidenceChannel(str, Enum):
    SOENANSTORE = "soenanStore"

    def __str__(self) -> str:
        return str(self.value)
