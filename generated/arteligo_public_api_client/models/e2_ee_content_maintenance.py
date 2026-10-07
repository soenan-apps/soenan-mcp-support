from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.e2_ee_content_maintenance_action import E2EeContentMaintenanceAction

T = TypeVar("T", bound="E2EeContentMaintenance")


@_attrs_define
class E2EeContentMaintenance:
    """
    Attributes:
        action (E2EeContentMaintenanceAction):
        migration_id (str):
        expected_checkpoint_revision (int):
        checkpoint_record_id (str):
        created_record_ids (list[str]):
    """

    action: E2EeContentMaintenanceAction
    migration_id: str
    expected_checkpoint_revision: int
    checkpoint_record_id: str
    created_record_ids: list[str]

    def to_dict(self) -> dict[str, Any]:
        action = self.action.value

        migration_id = self.migration_id

        expected_checkpoint_revision = self.expected_checkpoint_revision

        checkpoint_record_id = self.checkpoint_record_id

        created_record_ids = self.created_record_ids

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "action": action,
                "migration_id": migration_id,
                "expected_checkpoint_revision": expected_checkpoint_revision,
                "checkpoint_record_id": checkpoint_record_id,
                "created_record_ids": created_record_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        action = E2EeContentMaintenanceAction(d.pop("action"))

        migration_id = d.pop("migration_id")

        expected_checkpoint_revision = d.pop("expected_checkpoint_revision")

        checkpoint_record_id = d.pop("checkpoint_record_id")

        created_record_ids = cast(list[str], d.pop("created_record_ids"))

        e2_ee_content_maintenance = cls(
            action=action,
            migration_id=migration_id,
            expected_checkpoint_revision=expected_checkpoint_revision,
            checkpoint_record_id=checkpoint_record_id,
            created_record_ids=created_record_ids,
        )

        return e2_ee_content_maintenance
