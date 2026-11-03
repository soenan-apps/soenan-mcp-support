from enum import Enum


class OwnerCustodyOrganizationAdmissionKind(str, Enum):
    ORGANIZATION_ADMISSION = "organization_admission"

    def __str__(self) -> str:
        return str(self.value)
