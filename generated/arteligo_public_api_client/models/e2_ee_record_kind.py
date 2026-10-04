from enum import Enum


class E2EeRecordKind(str, Enum):
    CHAT = "chat"
    COMMENT = "comment"
    DIRECTORY = "directory"
    FILE = "file"
    PREVIEW = "preview"
    PROJECT = "project"
    SCHEDULE = "schedule"
    STAGE = "stage"
    SUBMISSION = "submission"

    def __str__(self) -> str:
        return str(self.value)
