from enum import Enum


class RealtimeProjectReviewInvalidatedType(str, Enum):
    PROJECT_REVIEW_INVALIDATED = "project_review_invalidated"

    def __str__(self) -> str:
        return str(self.value)
