from enum import Enum


class RealtimeProjectScheduleInvalidatedType(str, Enum):
    PROJECT_SCHEDULE_INVALIDATED = "project_schedule_invalidated"

    def __str__(self) -> str:
        return str(self.value)
