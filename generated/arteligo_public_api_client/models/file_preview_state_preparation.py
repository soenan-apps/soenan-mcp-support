from enum import Enum


class FilePreviewStatePreparation(str, Enum):
    CLIENT_UPLOAD = "client_upload"
    SERVER_JOB = "server_job"

    def __str__(self) -> str:
        return str(self.value)
