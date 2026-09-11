from enum import StrEnum


class StageProjectReferenceKind(StrEnum):
    STAGE = "stage"

    def __str__(self) -> str:
        return str(self.value)
