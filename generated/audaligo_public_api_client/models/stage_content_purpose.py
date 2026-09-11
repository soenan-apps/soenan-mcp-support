from enum import StrEnum


class StageContentPurpose(StrEnum):
    MIX = "mix"
    MODEL_3D = "model_3d"
    PRODUCTION_PLAN = "production_plan"
    SCRIPT = "script"
    VIDEO = "video"
    VOCAL = "vocal"

    def __str__(self) -> str:
        return str(self.value)
