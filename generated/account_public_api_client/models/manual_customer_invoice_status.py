from enum import Enum


class ManualCustomerInvoiceStatus(str, Enum):
    OPEN = "open"
    PAID = "paid"
    PARTIALLYPAID = "partiallyPaid"
    VOID = "void"

    def __str__(self) -> str:
        return str(self.value)
