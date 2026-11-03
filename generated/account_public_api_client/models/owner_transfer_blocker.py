from enum import Enum


class OwnerTransferBlocker(str, Enum):
    ABORT_PENDING = "abort_pending"
    AMBIGUOUS_OWNER_AUTHORITY = "ambiguous_owner_authority"
    APPLY_PENDING = "apply_pending"
    CANDIDATE_UNPREPARED = "candidate_unprepared"
    COVERAGE_INCOMPLETE = "coverage_incomplete"
    DEPENDENCY_CHANGED = "dependency_changed"
    DEPENDENCY_UNAVAILABLE = "dependency_unavailable"
    DEPENDENCY_UNKNOWN = "dependency_unknown"
    EMAIL_DELIVERY_UNAVAILABLE = "email_delivery_unavailable"
    EMAIL_PENDING = "email_pending"
    HANDOFF_BLOCKED = "handoff_blocked"
    OWNER_KEY_UNAVAILABLE = "owner_key_unavailable"
    RESERVATION_PENDING = "reservation_pending"
    REVISION_CONFLICT = "revision_conflict"
    SOURCE_MANIFEST_INCOMPLETE = "source_manifest_incomplete"
    TARGET_NOT_ELIGIBLE = "target_not_eligible"
    TRANSFER_IN_PROGRESS = "transfer_in_progress"
    VALUE_0 = ""

    def __str__(self) -> str:
        return str(self.value)
