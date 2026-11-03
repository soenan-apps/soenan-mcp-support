from enum import Enum


class ManualInvoiceContractValidity(str, Enum):
    FIXEDTERM = "fixedTerm"
    PERPETUAL = "perpetual"

    def __str__(self) -> str:
        return str(self.value)
