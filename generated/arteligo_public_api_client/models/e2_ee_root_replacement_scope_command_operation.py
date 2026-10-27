from enum import Enum


class E2EeRootReplacementScopeCommandOperation(str, Enum):
    ENVELOPES_SAVE = "envelopes_save"
    OWNER_ENVELOPES_SAVE = "owner_envelopes_save"
    OWNER_ROTATE_SCOPE = "owner_rotate_scope"
    ROTATE_SCOPE = "rotate_scope"

    def __str__(self) -> str:
        return str(self.value)
