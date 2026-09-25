from enum import Enum


class ProjectKeyRingContract(str, Enum):
    AUDALIGO_PROJECT_KEYRING = "audaligo.project-keyring"

    def __str__(self) -> str:
        return str(self.value)
