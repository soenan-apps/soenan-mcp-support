from enum import Enum


class OwnerKeyCustodyTargetPurpose(str, Enum):
    ACTOR = "actor"
    OWNER_CANDIDATE = "owner_candidate"
    PEER_TRUST_ISSUER = "peer_trust_issuer"
    PENDING_COMMAND_ISSUER = "pending_command_issuer"
    RETAINED_BINDING_ISSUER = "retained_binding_issuer"
    SCOPE_RECIPIENT = "scope_recipient"
    SOURCE_CREATOR = "source_creator"

    def __str__(self) -> str:
        return str(self.value)
