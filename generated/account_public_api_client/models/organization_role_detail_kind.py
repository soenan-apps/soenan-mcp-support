from enum import Enum


class OrganizationRoleDetailKind(str, Enum):
    BUILT_IN = "built_in"
    CUSTOM = "custom"

    def __str__(self) -> str:
        return str(self.value)
