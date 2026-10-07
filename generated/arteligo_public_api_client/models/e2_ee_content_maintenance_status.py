from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="E2EeContentMaintenanceStatus")


@_attrs_define
class E2EeContentMaintenanceStatus:
    """
    Attributes:
        migration_id (str):
        state (str):
        checkpoint_record_id (str):
        checkpoint_revision (int):
        lease_owner (str):
        lease_expires_at (int):
        created_record_count (int):
        source_scan_complete (bool): Whether the bounded scan of the migration source has completed.
    """

    migration_id: str
    state: str
    checkpoint_record_id: str
    checkpoint_revision: int
    lease_owner: str
    lease_expires_at: int
    created_record_count: int
    source_scan_complete: bool

    def to_dict(self) -> dict[str, Any]:
        migration_id = self.migration_id

        state = self.state

        checkpoint_record_id = self.checkpoint_record_id

        checkpoint_revision = self.checkpoint_revision

        lease_owner = self.lease_owner

        lease_expires_at = self.lease_expires_at

        created_record_count = self.created_record_count

        source_scan_complete = self.source_scan_complete

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "migration_id": migration_id,
                "state": state,
                "checkpoint_record_id": checkpoint_record_id,
                "checkpoint_revision": checkpoint_revision,
                "lease_owner": lease_owner,
                "lease_expires_at": lease_expires_at,
                "created_record_count": created_record_count,
                "source_scan_complete": source_scan_complete,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        migration_id = d.pop("migration_id")

        state = d.pop("state")

        checkpoint_record_id = d.pop("checkpoint_record_id")

        checkpoint_revision = d.pop("checkpoint_revision")

        lease_owner = d.pop("lease_owner")

        lease_expires_at = d.pop("lease_expires_at")

        created_record_count = d.pop("created_record_count")

        source_scan_complete = d.pop("source_scan_complete")

        e2_ee_content_maintenance_status = cls(
            migration_id=migration_id,
            state=state,
            checkpoint_record_id=checkpoint_record_id,
            checkpoint_revision=checkpoint_revision,
            lease_owner=lease_owner,
            lease_expires_at=lease_expires_at,
            created_record_count=created_record_count,
            source_scan_complete=source_scan_complete,
        )

        return e2_ee_content_maintenance_status
