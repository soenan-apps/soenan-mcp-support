from enum import Enum


class CommerceOverviewOwnerKind(str, Enum):
    GROUP = "group"
    PERSONAL = "personal"

    def __str__(self) -> str:
        return str(self.value)
