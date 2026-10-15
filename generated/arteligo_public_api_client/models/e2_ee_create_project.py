from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.e2_ee_content_record_write import E2EeContentRecordWrite
    from ..models.e2_ee_deletion_marker import E2EeDeletionMarker
    from ..models.e2_ee_envelope import E2EeEnvelope


T = TypeVar("T", bound="E2EeCreateProject")


@_attrs_define
class E2EeCreateProject:
    """
    Attributes:
        project_id (str):
        owner_org (str):
        participation_policy (str):
        envelopes (list[E2EeEnvelope]):
        records (list[E2EeContentRecordWrite | E2EeDeletionMarker]):
    """

    project_id: str
    owner_org: str
    participation_policy: str
    envelopes: list[E2EeEnvelope]
    records: list[E2EeContentRecordWrite | E2EeDeletionMarker]

    def to_dict(self) -> dict[str, Any]:
        from ..models.e2_ee_content_record_write import E2EeContentRecordWrite

        project_id = self.project_id

        owner_org = self.owner_org

        participation_policy = self.participation_policy

        envelopes = []
        for envelopes_item_data in self.envelopes:
            envelopes_item = envelopes_item_data.to_dict()
            envelopes.append(envelopes_item)

        records = []
        for records_item_data in self.records:
            records_item: dict[str, Any]
            if isinstance(records_item_data, E2EeContentRecordWrite):
                records_item = records_item_data.to_dict()
            else:
                records_item = records_item_data.to_dict()

            records.append(records_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "project_id": project_id,
                "owner_org": owner_org,
                "participation_policy": participation_policy,
                "envelopes": envelopes,
                "records": records,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_content_record_write import E2EeContentRecordWrite
        from ..models.e2_ee_deletion_marker import E2EeDeletionMarker
        from ..models.e2_ee_envelope import E2EeEnvelope

        d = dict(src_dict)
        project_id = d.pop("project_id")

        owner_org = d.pop("owner_org")

        participation_policy = d.pop("participation_policy")

        envelopes = []
        _envelopes = d.pop("envelopes")
        for envelopes_item_data in _envelopes:
            envelopes_item = E2EeEnvelope.from_dict(envelopes_item_data)

            envelopes.append(envelopes_item)

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

        e2_ee_create_project = cls(
            project_id=project_id,
            owner_org=owner_org,
            participation_policy=participation_policy,
            envelopes=envelopes,
            records=records,
        )

        return e2_ee_create_project
