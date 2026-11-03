from enum import Enum


class OwnerKeyScopeAuthorizationTargetBasis(str, Enum):
    PRODUCT_ENTITLEMENT = "product_entitlement"
    PROJECT_SPONSORSHIP = "project_sponsorship"

    def __str__(self) -> str:
        return str(self.value)
