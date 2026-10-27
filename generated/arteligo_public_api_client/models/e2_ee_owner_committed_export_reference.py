from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="E2EeOwnerCommittedExportReference")


@_attrs_define
class E2EeOwnerCommittedExportReference:
    """Locator for one exact committed export from the enclosing selected binding. Verify the immutable Account selection
    and decision, original source authority, preparation and manifest before accepting source history. This reference
    grants no independent authority.

        Attributes:
            operation_id (str):
            successor_binding_digest (str):
            source_manifest_id (str):
            source_manifest_digest (str):
    """

    operation_id: str
    successor_binding_digest: str
    source_manifest_id: str
    source_manifest_digest: str

    def to_dict(self) -> dict[str, Any]:
        operation_id = self.operation_id

        successor_binding_digest = self.successor_binding_digest

        source_manifest_id = self.source_manifest_id

        source_manifest_digest = self.source_manifest_digest

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "operation_id": operation_id,
                "successor_binding_digest": successor_binding_digest,
                "source_manifest_id": source_manifest_id,
                "source_manifest_digest": source_manifest_digest,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        operation_id = d.pop("operation_id")

        successor_binding_digest = d.pop("successor_binding_digest")

        source_manifest_id = d.pop("source_manifest_id")

        source_manifest_digest = d.pop("source_manifest_digest")

        e2_ee_owner_committed_export_reference = cls(
            operation_id=operation_id,
            successor_binding_digest=successor_binding_digest,
            source_manifest_id=source_manifest_id,
            source_manifest_digest=source_manifest_digest,
        )

        return e2_ee_owner_committed_export_reference
