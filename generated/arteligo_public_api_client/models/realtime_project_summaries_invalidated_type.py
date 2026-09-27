from enum import Enum


class RealtimeProjectSummariesInvalidatedType(str, Enum):
    PROJECT_SUMMARIES_INVALIDATED = "project_summaries_invalidated"

    def __str__(self) -> str:
        return str(self.value)
