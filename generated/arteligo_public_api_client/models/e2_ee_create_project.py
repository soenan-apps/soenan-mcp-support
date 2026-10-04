from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.e2_ee_envelope import E2EeEnvelope
    from ..models.e2_ee_record_write import E2EeRecordWrite


T = TypeVar("T", bound="E2EeCreateProject")


@_attrs_define
class E2EeCreateProject:
    """
    Attributes:
        project_id (str):
        owner_org (str):
        participation_policy (str):
        envelopes (list[E2EeEnvelope]):
        records (list[E2EeRecordWrite]):
    """

    project_id: str
    owner_org: str
    participation_policy: str
    envelopes: list[E2EeEnvelope]
    records: list[E2EeRecordWrite]

    def to_dict(self) -> dict[str, Any]:
        project_id = self.project_id

        owner_org = self.owner_org

        participation_policy = self.participation_policy

        envelopes = []
        for envelopes_item_data in self.envelopes:
            envelopes_item = envelopes_item_data.to_dict()
            envelopes.append(envelopes_item)

        records = []
        for records_item_data in self.records:
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
        from ..models.e2_ee_envelope import E2EeEnvelope
        from ..models.e2_ee_record_write import E2EeRecordWrite

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
            records_item = E2EeRecordWrite.from_dict(records_item_data)

            records.append(records_item)

        e2_ee_create_project = cls(
            project_id=project_id,
            owner_org=owner_org,
            participation_policy=participation_policy,
            envelopes=envelopes,
            records=records,
        )

        return e2_ee_create_project
