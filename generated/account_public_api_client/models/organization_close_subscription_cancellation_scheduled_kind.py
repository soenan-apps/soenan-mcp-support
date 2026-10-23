from enum import Enum


class OrganizationCloseSubscriptionCancellationScheduledKind(str, Enum):
    SUBSCRIPTION_CANCELLATION_SCHEDULED = "subscription_cancellation_scheduled"

    def __str__(self) -> str:
        return str(self.value)
