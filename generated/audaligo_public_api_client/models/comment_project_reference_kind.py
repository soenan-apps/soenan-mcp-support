from enum import StrEnum


class CommentProjectReferenceKind(StrEnum):
    COMMENT = "comment"

    def __str__(self) -> str:
        return str(self.value)
