from enum import Enum


class E2EeRootReplacementInputEventKind(str, Enum):
    APPLY_HEADER = "apply_header"
    COMPANION_ADMISSION = "companion_admission"
    COMPLETE = "complete"
    FRAGMENT = "fragment"
    GATE = "gate"
    KEYRING = "keyring"
    OWNER_CANDIDATE = "owner_candidate"
    OWNER_KEY = "owner_key"
    PENDING_COMMAND = "pending_command"
    PREPARATION = "preparation"
    PREPARE_HEADER = "prepare_header"
    PROTECTED_SOURCE = "protected_source"
    REFERENCE = "reference"
    RETAINED_BINDING = "retained_binding"
    ROOT_COMMAND = "root_command"
    SCOPE_COMMAND = "scope_command"
    SOURCE_SUBMISSION = "source_submission"

    def __str__(self) -> str:
        return str(self.value)
