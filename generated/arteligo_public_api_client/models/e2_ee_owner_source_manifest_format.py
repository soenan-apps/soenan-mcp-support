from enum import Enum


class E2EeOwnerSourceManifestFormat(str, Enum):
    PROJECT_INDEX_V1 = "project_index_v1"

    def __str__(self) -> str:
        return str(self.value)
