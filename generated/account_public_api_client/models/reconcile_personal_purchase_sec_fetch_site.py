from enum import Enum


class ReconcilePersonalPurchaseSecFetchSite(str, Enum):
    SAME_ORIGIN = "same-origin"

    def __str__(self) -> str:
        return str(self.value)
