from enum import Enum


class RealtimeProjectChangesSubscribedType(str, Enum):
    PROJECT_CHANGES_SUBSCRIBED = "project_changes_subscribed"

    def __str__(self) -> str:
        return str(self.value)
