from enum import Enum


class E2EeKeyOperationPendingCommandOperation(str, Enum):
    DEVICE_ADD_BY_KEY = "device_add_by_key"
    ENVELOPES_SAVE = "envelopes_save"
    OWNER_CANDIDATE_OFFER = "owner_candidate_offer"
    OWNER_CUSTODY_INVALIDATE = "owner_custody_invalidate"
    OWNER_ENVELOPES_SAVE = "owner_envelopes_save"
    OWNER_GATE_CREATE = "owner_gate_create"
    OWNER_HANDOFF_PREPARE = "owner_handoff_prepare"
    OWNER_KEYRING_SAVE = "owner_keyring_save"
    OWNER_KEY_REGISTER = "owner_key_register"
    OWNER_ROTATE_SCOPE = "owner_rotate_scope"
    OWNER_SOURCE_MANIFEST = "owner_source_manifest"
    RECOVERY_ROTATE = "recovery_rotate"
    ROTATE_SCOPE = "rotate_scope"

    def __str__(self) -> str:
        return str(self.value)
