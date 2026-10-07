from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.e2_ee_project import E2EeProject
    from ..models.e2_ee_record_change import E2EeRecordChange


T = TypeVar("T", bound="E2EeChangesPage")


@_attrs_define
class E2EeChangesPage:
    """
    Attributes:
        changes (list[E2EeRecordChange]):
        cursor (int):
        has_more (bool):
        minimum_cursor (int):
        metadata (E2EeProject):
        server_time (int):
    """

    changes: list[E2EeRecordChange]
    cursor: int
    has_more: bool
    minimum_cursor: int
    metadata: E2EeProject
    server_time: int

    def to_dict(self) -> dict[str, Any]:
        changes = []
        for changes_item_data in self.changes:
            changes_item = changes_item_data.to_dict()
            changes.append(changes_item)

        cursor = self.cursor

        has_more = self.has_more

        minimum_cursor = self.minimum_cursor

        metadata = self.metadata.to_dict()

        server_time = self.server_time

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "changes": changes,
                "cursor": cursor,
                "has_more": has_more,
                "minimum_cursor": minimum_cursor,
                "metadata": metadata,
                "server_time": server_time,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_project import E2EeProject
        from ..models.e2_ee_record_change import E2EeRecordChange

        d = dict(src_dict)
        changes = []
        _changes = d.pop("changes")
        for changes_item_data in _changes:
            changes_item = E2EeRecordChange.from_dict(changes_item_data)

            changes.append(changes_item)

        cursor = d.pop("cursor")

        has_more = d.pop("has_more")

        minimum_cursor = d.pop("minimum_cursor")

        metadata = E2EeProject.from_dict(d.pop("metadata"))

        server_time = d.pop("server_time")

        e2_ee_changes_page = cls(
            changes=changes,
            cursor=cursor,
            has_more=has_more,
            minimum_cursor=minimum_cursor,
            metadata=metadata,
            server_time=server_time,
        )

        return e2_ee_changes_page
