from enum import Enum


class CommentReplyProjectReferenceKind(str, Enum):
    COMMENT_REPLY = "comment_reply"

    def __str__(self) -> str:
        return str(self.value)
