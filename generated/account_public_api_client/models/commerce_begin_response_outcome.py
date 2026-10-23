from enum import Enum


class CommerceBeginResponseOutcome(str, Enum):
    ACCOUNTCLOSED = "accountClosed"
    ALREADYSUBSCRIBED = "alreadySubscribed"
    OWNERMISMATCH = "ownerMismatch"
    PREPARED = "prepared"
    PROVIDERPENDING = "providerPending"
    PURCHASEINPROGRESS = "purchaseInProgress"
    RECONCILIATIONPENDING = "reconciliationPending"
    RESUME = "resume"

    def __str__(self) -> str:
        return str(self.value)
