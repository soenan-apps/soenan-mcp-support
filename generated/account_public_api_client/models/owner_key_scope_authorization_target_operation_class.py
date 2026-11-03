from enum import Enum


class OwnerKeyScopeAuthorizationTargetOperationClass(str, Enum):
    INTERACTIVE_MUTATION = "interactive_mutation"
    INTERACTIVE_READ = "interactive_read"

    def __str__(self) -> str:
        return str(self.value)
