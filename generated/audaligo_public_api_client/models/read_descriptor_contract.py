from enum import Enum


class ReadDescriptorContract(str, Enum):
    AUDALIGO_MANAGED_PROJECT_FILE_READ_DESCRIPTOR = "audaligo.managed-project-file-read-descriptor"

    def __str__(self) -> str:
        return str(self.value)
