from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="OwnerSourceSelection")


@_attrs_define
class OwnerSourceSelection:
    """The latest committed content-transfer selection at this authority's historical ownership-revision cutoff. No-content
    transfers and key registration do not erase it.

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
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        operation_id = d.pop("operation_id")

        successor_binding_digest = d.pop("successor_binding_digest")

        source_manifest_id = d.pop("source_manifest_id")

        source_manifest_digest = d.pop("source_manifest_digest")

        owner_source_selection = cls(
            operation_id=operation_id,
            successor_binding_digest=successor_binding_digest,
            source_manifest_id=source_manifest_id,
            source_manifest_digest=source_manifest_digest,
        )

        return owner_source_selection
