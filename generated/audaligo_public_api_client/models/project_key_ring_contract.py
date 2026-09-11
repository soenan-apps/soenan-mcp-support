from enum import StrEnum


class ProjectKeyRingContract(StrEnum):
    AUDALIGO_PROJECT_KEYRING = "audaligo.project-keyring"

    def __str__(self) -> str:
        return str(self.value)
