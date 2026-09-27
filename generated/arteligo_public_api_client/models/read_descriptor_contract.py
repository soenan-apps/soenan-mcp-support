from enum import Enum


class ReadDescriptorContract(str, Enum):
    ARTELIGO_MANAGED_PROJECT_FILE_READ_DESCRIPTOR = (
        "arteligo.managed-project-file-read-descriptor"
    )

    def __str__(self) -> str:
        return str(self.value)
