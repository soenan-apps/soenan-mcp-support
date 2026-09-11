from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="ProjectEntryDeletionResponse")


@_attrs_define
class ProjectEntryDeletionResponse:
    """
    Attributes:
        deleted_entry_id (str):
    """

    deleted_entry_id: str

    def to_dict(self) -> dict[str, Any]:
        deleted_entry_id = self.deleted_entry_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "deletedEntryId": deleted_entry_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        deleted_entry_id = d.pop("deletedEntryId")

        project_entry_deletion_response = cls(
            deleted_entry_id=deleted_entry_id,
        )

        return project_entry_deletion_response
