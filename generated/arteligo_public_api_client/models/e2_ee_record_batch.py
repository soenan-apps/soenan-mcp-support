from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.e2_ee_record_batch_format_version import E2EeRecordBatchFormatVersion
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.e2_ee_content_maintenance import E2EeContentMaintenance
    from ..models.e2_ee_content_record_write import E2EeContentRecordWrite
    from ..models.e2_ee_deletion_marker import E2EeDeletionMarker
    from ..models.e2_ee_record_precondition import E2EeRecordPrecondition


T = TypeVar("T", bound="E2EeRecordBatch")


@_attrs_define
class E2EeRecordBatch:
    """A newly accepted batch containing any metadata-only deletion marker must be RFC 8785 canonical JSON with the
    complete closed schema below; unknown fields, opaque marker payloads and noncanonical bytes are rejected. The server
    never normalizes or resigns the command. Existing content-only first acceptance, stored historical evidence and
    successful receipt replay preserve their original signed bytes. Deletion markers commit no content usage; prior
    charged content retires through the existing atomic usage/outbox transaction.

        Attributes:
            format_version (E2EeRecordBatchFormatVersion): Version 3 is required when any record has kind chat or comment,
                including mixed batches. All other content batches use version 2. A version-2 conversation write receives 409
                content_format_update_required; missing or otherwise invalid versions receive 400 invalid_request. Successful
                stored receipts replay their exact original signed bytes.
            expires_at (int): UNIX seconds; first use must be unexpired and at most 30 days ahead of the database clock.
            scope_id (str):
            records (list[E2EeContentRecordWrite | E2EeDeletionMarker]):
            deleted_objects (list[str] | Unset):
            preconditions (list[E2EeRecordPrecondition] | Unset):
            maintenance (E2EeContentMaintenance | Unset):
    """

    format_version: E2EeRecordBatchFormatVersion
    expires_at: int
    scope_id: str
    records: list[E2EeContentRecordWrite | E2EeDeletionMarker]
    deleted_objects: list[str] | Unset = UNSET
    preconditions: list[E2EeRecordPrecondition] | Unset = UNSET
    maintenance: E2EeContentMaintenance | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        from ..models.e2_ee_content_record_write import E2EeContentRecordWrite

        format_version = self.format_version.value

        expires_at = self.expires_at

        scope_id = self.scope_id

        records = []
        for records_item_data in self.records:
            records_item: dict[str, Any]
            if isinstance(records_item_data, E2EeContentRecordWrite):
                records_item = records_item_data.to_dict()
            else:
                records_item = records_item_data.to_dict()

            records.append(records_item)

        deleted_objects: list[str] | Unset = UNSET
        if not isinstance(self.deleted_objects, Unset):
            deleted_objects = self.deleted_objects

        preconditions: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.preconditions, Unset):
            preconditions = []
            for preconditions_item_data in self.preconditions:
                preconditions_item = preconditions_item_data.to_dict()
                preconditions.append(preconditions_item)

        maintenance: dict[str, Any] | Unset = UNSET
        if not isinstance(self.maintenance, Unset):
            maintenance = self.maintenance.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "format_version": format_version,
                "expires_at": expires_at,
                "scope_id": scope_id,
                "records": records,
            }
        )
        if deleted_objects is not UNSET:
            field_dict["deleted_objects"] = deleted_objects
        if preconditions is not UNSET:
            field_dict["preconditions"] = preconditions
        if maintenance is not UNSET:
            field_dict["maintenance"] = maintenance

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_content_maintenance import E2EeContentMaintenance
        from ..models.e2_ee_content_record_write import E2EeContentRecordWrite
        from ..models.e2_ee_deletion_marker import E2EeDeletionMarker
        from ..models.e2_ee_record_precondition import E2EeRecordPrecondition

        d = dict(src_dict)
        format_version = E2EeRecordBatchFormatVersion(d.pop("format_version"))

        expires_at = d.pop("expires_at")

        scope_id = d.pop("scope_id")

        records = []
        _records = d.pop("records")
        for records_item_data in _records:

            def _parse_records_item(
                data: object,
            ) -> E2EeContentRecordWrite | E2EeDeletionMarker:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_e2_ee_record_write_type_0 = (
                        E2EeContentRecordWrite.from_dict(data)
                    )

                    return componentsschemas_e2_ee_record_write_type_0
                except (TypeError, ValueError, AttributeError, KeyError):
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_e2_ee_record_write_type_1 = (
                    E2EeDeletionMarker.from_dict(data)
                )

                return componentsschemas_e2_ee_record_write_type_1

            records_item = _parse_records_item(records_item_data)

            records.append(records_item)

        deleted_objects = cast(list[str], d.pop("deleted_objects", UNSET))

        _preconditions = d.pop("preconditions", UNSET)
        preconditions: list[E2EeRecordPrecondition] | Unset = UNSET
        if _preconditions is not UNSET:
            preconditions = []
            for preconditions_item_data in _preconditions:
                preconditions_item = E2EeRecordPrecondition.from_dict(
                    preconditions_item_data
                )

                preconditions.append(preconditions_item)

        _maintenance = d.pop("maintenance", UNSET)
        maintenance: E2EeContentMaintenance | Unset
        if isinstance(_maintenance, Unset):
            maintenance = UNSET
        else:
            maintenance = E2EeContentMaintenance.from_dict(_maintenance)

        e2_ee_record_batch = cls(
            format_version=format_version,
            expires_at=expires_at,
            scope_id=scope_id,
            records=records,
            deleted_objects=deleted_objects,
            preconditions=preconditions,
            maintenance=maintenance,
        )

        return e2_ee_record_batch
