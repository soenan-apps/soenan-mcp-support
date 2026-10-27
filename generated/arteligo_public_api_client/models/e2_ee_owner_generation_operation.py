from enum import Enum


class E2EeOwnerGenerationOperation(str, Enum):
    ORGANIZATION_CREATE = "organization_create"
    OWNER_ROTATE_SCOPE = "owner_rotate_scope"
    PROJECT_CREATE = "project_create"
    ROTATE_SCOPE = "rotate_scope"

    def __str__(self) -> str:
        return str(self.value)
