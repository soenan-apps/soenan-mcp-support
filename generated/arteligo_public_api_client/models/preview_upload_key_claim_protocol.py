from enum import Enum


class PreviewUploadKeyClaimProtocol(str, Enum):
    ARTELIGO_FILE_KEY_CLAIM_V1 = "arteligo.file-key-claim.v1"

    def __str__(self) -> str:
        return str(self.value)
