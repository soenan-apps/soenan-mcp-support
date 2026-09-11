from enum import StrEnum


class ReadDescriptorContract(StrEnum):
    AUDALIGO_MANAGED_PROJECT_FILE_READ_DESCRIPTOR = (
        "audaligo.managed-project-file-read-descriptor"
    )

    def __str__(self) -> str:
        return str(self.value)
