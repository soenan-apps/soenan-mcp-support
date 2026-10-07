from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.e2_ee_immutable_page_commands import E2EeImmutablePageCommands
    from ..models.e2_ee_project import E2EeProject
    from ..models.e2_ee_read_response import E2EeReadResponse
    from ..models.e2_ee_record_reference import E2EeRecordReference


T = TypeVar("T", bound="E2EeImmutablePage")


@_attrs_define
class E2EeImmutablePage:
    """
    Attributes:
        records (list[E2EeRecordReference]):
        commands (E2EeImmutablePageCommands):
        cursor (int): Last returned creation cursor, or the requested after cursor when empty.
        snapshot_cursor (int): Fixed inclusive upper cursor reused for all continuation requests.
        has_more (bool):
        server_time (int):
        metadata (E2EeProject | Unset):
        key_context (E2EeReadResponse | Unset):
    """

    records: list[E2EeRecordReference]
    commands: E2EeImmutablePageCommands
    cursor: int
    snapshot_cursor: int
    has_more: bool
    server_time: int
    metadata: E2EeProject | Unset = UNSET
    key_context: E2EeReadResponse | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        records = []
        for records_item_data in self.records:
            records_item = records_item_data.to_dict()
            records.append(records_item)

        commands = self.commands.to_dict()

        cursor = self.cursor

        snapshot_cursor = self.snapshot_cursor

        has_more = self.has_more

        server_time = self.server_time

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        key_context: dict[str, Any] | Unset = UNSET
        if not isinstance(self.key_context, Unset):
            key_context = self.key_context.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "records": records,
                "commands": commands,
                "cursor": cursor,
                "snapshot_cursor": snapshot_cursor,
                "has_more": has_more,
                "server_time": server_time,
            }
        )
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if key_context is not UNSET:
            field_dict["key_context"] = key_context

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_immutable_page_commands import E2EeImmutablePageCommands
        from ..models.e2_ee_project import E2EeProject
        from ..models.e2_ee_read_response import E2EeReadResponse
        from ..models.e2_ee_record_reference import E2EeRecordReference

        d = dict(src_dict)
        records = []
        _records = d.pop("records")
        for records_item_data in _records:
            records_item = E2EeRecordReference.from_dict(records_item_data)

            records.append(records_item)

        commands = E2EeImmutablePageCommands.from_dict(d.pop("commands"))

        cursor = d.pop("cursor")

        snapshot_cursor = d.pop("snapshot_cursor")

        has_more = d.pop("has_more")

        server_time = d.pop("server_time")

        _metadata = d.pop("metadata", UNSET)
        metadata: E2EeProject | Unset
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = E2EeProject.from_dict(_metadata)

        _key_context = d.pop("key_context", UNSET)
        key_context: E2EeReadResponse | Unset
        if isinstance(_key_context, Unset):
            key_context = UNSET
        else:
            key_context = E2EeReadResponse.from_dict(_key_context)

        e2_ee_immutable_page = cls(
            records=records,
            commands=commands,
            cursor=cursor,
            snapshot_cursor=snapshot_cursor,
            has_more=has_more,
            server_time=server_time,
            metadata=metadata,
            key_context=key_context,
        )

        return e2_ee_immutable_page
