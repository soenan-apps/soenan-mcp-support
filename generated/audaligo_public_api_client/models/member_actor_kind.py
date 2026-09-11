from enum import StrEnum


class MemberActorKind(StrEnum):
    MEMBER = "member"

    def __str__(self) -> str:
        return str(self.value)
