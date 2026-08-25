from enum import Enum


class FileKeyClaimProtocol(str, Enum):
    AUDALIGO_FILE_KEY_CLAIM_V1 = "audaligo.file-key-claim.v1"

    def __str__(self) -> str:
        return str(self.value)
