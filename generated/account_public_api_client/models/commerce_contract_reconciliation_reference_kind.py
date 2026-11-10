from enum import Enum


class CommerceContractReconciliationReferenceKind(str, Enum):
    CONTRACTRECONCILIATION = "contractReconciliation"

    def __str__(self) -> str:
        return str(self.value)
