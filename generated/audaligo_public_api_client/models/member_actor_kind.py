from enum import Enum


class MemberActorKind(str, Enum):
    MEMBER = "member"

    def __str__(self) -> str:
        return str(self.value)
