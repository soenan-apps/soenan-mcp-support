from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.e2_ee_deletion_marker_record import E2EeDeletionMarkerRecord
    from ..models.e2_ee_encrypted_record import E2EeEncryptedRecord


T = TypeVar("T", bound="E2EeRecordPage")


@_attrs_define
class E2EeRecordPage:
    """
    Attributes:
        records (list[E2EeDeletionMarkerRecord | E2EeEncryptedRecord]):
        cursor (int):
        has_more (bool):
    """

    records: list[E2EeDeletionMarkerRecord | E2EeEncryptedRecord]
    cursor: int
    has_more: bool

    def to_dict(self) -> dict[str, Any]:
        from ..models.e2_ee_encrypted_record import E2EeEncryptedRecord

        records = []
        for records_item_data in self.records:
            records_item: dict[str, Any]
            if isinstance(records_item_data, E2EeEncryptedRecord):
                records_item = records_item_data.to_dict()
            else:
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
        from ..models.e2_ee_deletion_marker_record import E2EeDeletionMarkerRecord
        from ..models.e2_ee_encrypted_record import E2EeEncryptedRecord

        d = dict(src_dict)
        records = []
        _records = d.pop("records")
        for records_item_data in _records:

            def _parse_records_item(
                data: object,
            ) -> E2EeDeletionMarkerRecord | E2EeEncryptedRecord:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_e2_ee_record_type_0 = (
                        E2EeEncryptedRecord.from_dict(data)
                    )

                    return componentsschemas_e2_ee_record_type_0
                except (TypeError, ValueError, AttributeError, KeyError):
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_e2_ee_record_type_1 = (
                    E2EeDeletionMarkerRecord.from_dict(data)
                )

                return componentsschemas_e2_ee_record_type_1

            records_item = _parse_records_item(records_item_data)

            records.append(records_item)

        cursor = d.pop("cursor")

        has_more = d.pop("has_more")

        e2_ee_record_page = cls(
            records=records,
            cursor=cursor,
            has_more=has_more,
        )

        return e2_ee_record_page
