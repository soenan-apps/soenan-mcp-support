from enum import Enum


class OwnerOrganizationAdmissionSignedFieldsOperation(str, Enum):
    ENVELOPES_SAVE = "envelopes_save"

    def __str__(self) -> str:
        return str(self.value)
