from enum import Enum


class RealtimeProjectChangesCatchUpRequiredType(str, Enum):
    PROJECT_CHANGES_CATCH_UP_REQUIRED = "project_changes_catch_up_required"

    def __str__(self) -> str:
        return str(self.value)
