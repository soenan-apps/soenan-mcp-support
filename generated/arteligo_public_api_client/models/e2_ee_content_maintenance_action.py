from enum import Enum


class E2EeContentMaintenanceAction(str, Enum):
    ABORT = "abort"
    BEGIN = "begin"
    COMPLETE = "complete"
    PROGRESS = "progress"

    def __str__(self) -> str:
        return str(self.value)
