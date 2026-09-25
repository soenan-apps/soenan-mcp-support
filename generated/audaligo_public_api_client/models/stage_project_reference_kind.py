from enum import Enum


class StageProjectReferenceKind(str, Enum):
    STAGE = "stage"

    def __str__(self) -> str:
        return str(self.value)
