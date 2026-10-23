from enum import Enum


class E2EeOwnerSourceCommandIssuerOperation(str, Enum):
    PEER_TRUST = "peer_trust"
    PROJECT_CREATE = "project_create"

    def __str__(self) -> str:
        return str(self.value)
