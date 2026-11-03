from enum import Enum


class ManualCustomerRefundEffect(str, Enum):
    KEEP = "keep"
    TERMINATEAT = "terminateAt"

    def __str__(self) -> str:
        return str(self.value)
