from enum import StrEnum


class CommentReplyProjectReferenceKind(StrEnum):
    COMMENT_REPLY = "comment_reply"

    def __str__(self) -> str:
        return str(self.value)
