from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.e2_ee_record import E2EeRecord


T = TypeVar("T", bound="E2EeRecordPage")


@_attrs_define
class E2EeRecordPage:
    """
    Attributes:
        records (list[E2EeRecord]):
        cursor (int):
        has_more (bool):
    """

    records: list[E2EeRecord]
    cursor: int
    has_more: bool

    def to_dict(self) -> dict[str, Any]:
        records = []
        for records_item_data in self.records:
            records_item = records_item_data.to_dict()
            records.append(records_item)

        cursor = self.cursor

        has_more = self.has_more

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "records": records,
                "cursor": cursor,
                "has_more": has_more,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_record import E2EeRecord

        d = dict(src_dict)
        records = []
        _records = d.pop("records")
        for records_item_data in _records:
            records_item = E2EeRecord.from_dict(records_item_data)

            records.append(records_item)

        cursor = d.pop("cursor")

        has_more = d.pop("has_more")

        e2_ee_record_page = cls(
            records=records,
            cursor=cursor,
            has_more=has_more,
        )

        return e2_ee_record_page
