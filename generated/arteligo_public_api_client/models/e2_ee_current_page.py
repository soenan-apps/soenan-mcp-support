from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.e2_ee_current_page_commands import E2EeCurrentPageCommands
    from ..models.e2_ee_project import E2EeProject
    from ..models.e2_ee_read_response import E2EeReadResponse
    from ..models.e2_ee_record_reference import E2EeRecordReference


T = TypeVar("T", bound="E2EeCurrentPage")


@_attrs_define
class E2EeCurrentPage:
    """
    Attributes:
        records (list[E2EeRecordReference]):
        commands (E2EeCurrentPageCommands):
        cursor (int):
        has_more (bool):
        server_time (int):
        next_record_id (str | Unset):
        metadata (E2EeProject | Unset):
        key_context (E2EeReadResponse | Unset):
    """

    records: list[E2EeRecordReference]
    commands: E2EeCurrentPageCommands
    cursor: int
    has_more: bool
    server_time: int
    next_record_id: str | Unset = UNSET
    metadata: E2EeProject | Unset = UNSET
    key_context: E2EeReadResponse | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        records = []
        for records_item_data in self.records:
            records_item = records_item_data.to_dict()
            records.append(records_item)

        commands = self.commands.to_dict()

        cursor = self.cursor

        has_more = self.has_more

        server_time = self.server_time

        next_record_id = self.next_record_id

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
                "has_more": has_more,
                "server_time": server_time,
            }
        )
        if next_record_id is not UNSET:
            field_dict["next_record_id"] = next_record_id
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if key_context is not UNSET:
            field_dict["key_context"] = key_context

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_current_page_commands import E2EeCurrentPageCommands
        from ..models.e2_ee_project import E2EeProject
        from ..models.e2_ee_read_response import E2EeReadResponse
        from ..models.e2_ee_record_reference import E2EeRecordReference

        d = dict(src_dict)
        records = []
        _records = d.pop("records")
        for records_item_data in _records:
            records_item = E2EeRecordReference.from_dict(records_item_data)

            records.append(records_item)

        commands = E2EeCurrentPageCommands.from_dict(d.pop("commands"))

        cursor = d.pop("cursor")

        has_more = d.pop("has_more")

        server_time = d.pop("server_time")

        next_record_id = d.pop("next_record_id", UNSET)

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

        e2_ee_current_page = cls(
            records=records,
            commands=commands,
            cursor=cursor,
            has_more=has_more,
            server_time=server_time,
            next_record_id=next_record_id,
            metadata=metadata,
            key_context=key_context,
        )

        return e2_ee_current_page
