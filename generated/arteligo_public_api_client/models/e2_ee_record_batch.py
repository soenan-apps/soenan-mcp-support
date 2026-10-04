from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.e2_ee_record_write import E2EeRecordWrite


T = TypeVar("T", bound="E2EeRecordBatch")


@_attrs_define
class E2EeRecordBatch:
    """
    Attributes:
        scope_id (str):
        records (list[E2EeRecordWrite]):
        deleted_objects (list[str] | Unset):
    """

    scope_id: str
    records: list[E2EeRecordWrite]
    deleted_objects: list[str] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        scope_id = self.scope_id

        records = []
        for records_item_data in self.records:
            records_item = records_item_data.to_dict()
            records.append(records_item)

        deleted_objects: list[str] | Unset = UNSET
        if not isinstance(self.deleted_objects, Unset):
            deleted_objects = self.deleted_objects

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "scope_id": scope_id,
                "records": records,
            }
        )
        if deleted_objects is not UNSET:
            field_dict["deleted_objects"] = deleted_objects

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_record_write import E2EeRecordWrite

        d = dict(src_dict)
        scope_id = d.pop("scope_id")

        records = []
        _records = d.pop("records")
        for records_item_data in _records:
            records_item = E2EeRecordWrite.from_dict(records_item_data)

            records.append(records_item)

        deleted_objects = cast(list[str], d.pop("deleted_objects", UNSET))

        e2_ee_record_batch = cls(
            scope_id=scope_id,
            records=records,
            deleted_objects=deleted_objects,
        )

        return e2_ee_record_batch
