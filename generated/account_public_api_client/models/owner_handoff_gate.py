from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="OwnerHandoffGate")


@_attrs_define
class OwnerHandoffGate:
    """
    Attributes:
        gate_id (str):
        organization_id (str):
        preparation_id (str):
        candidate_id (str):
        ownership_revision (int):
        source_key_epoch (int):
        source_binding_digest (str):
        offer_digest (str):
        source_manifest_id (str):
        source_manifest_digest (str):
        history_manifest_digest (str):
        public_key (str):
    """

    gate_id: str
    organization_id: str
    preparation_id: str
    candidate_id: str
    ownership_revision: int
    source_key_epoch: int
    source_binding_digest: str
    offer_digest: str
    source_manifest_id: str
    source_manifest_digest: str
    history_manifest_digest: str
    public_key: str

    def to_dict(self) -> dict[str, Any]:
        gate_id = self.gate_id

        organization_id = self.organization_id

        preparation_id = self.preparation_id

        candidate_id = self.candidate_id

        ownership_revision = self.ownership_revision

        source_key_epoch = self.source_key_epoch

        source_binding_digest = self.source_binding_digest

        offer_digest = self.offer_digest

        source_manifest_id = self.source_manifest_id

        source_manifest_digest = self.source_manifest_digest

        history_manifest_digest = self.history_manifest_digest

        public_key = self.public_key

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "gate_id": gate_id,
                "organization_id": organization_id,
                "preparation_id": preparation_id,
                "candidate_id": candidate_id,
                "ownership_revision": ownership_revision,
                "source_key_epoch": source_key_epoch,
                "source_binding_digest": source_binding_digest,
                "offer_digest": offer_digest,
                "source_manifest_id": source_manifest_id,
                "source_manifest_digest": source_manifest_digest,
                "history_manifest_digest": history_manifest_digest,
                "public_key": public_key,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        gate_id = d.pop("gate_id")

        organization_id = d.pop("organization_id")

        preparation_id = d.pop("preparation_id")

        candidate_id = d.pop("candidate_id")

        ownership_revision = d.pop("ownership_revision")

        source_key_epoch = d.pop("source_key_epoch")

        source_binding_digest = d.pop("source_binding_digest")

        offer_digest = d.pop("offer_digest")

        source_manifest_id = d.pop("source_manifest_id")

        source_manifest_digest = d.pop("source_manifest_digest")

        history_manifest_digest = d.pop("history_manifest_digest")

        public_key = d.pop("public_key")

        owner_handoff_gate = cls(
            gate_id=gate_id,
            organization_id=organization_id,
            preparation_id=preparation_id,
            candidate_id=candidate_id,
            ownership_revision=ownership_revision,
            source_key_epoch=source_key_epoch,
            source_binding_digest=source_binding_digest,
            offer_digest=offer_digest,
            source_manifest_id=source_manifest_id,
            source_manifest_digest=source_manifest_digest,
            history_manifest_digest=history_manifest_digest,
            public_key=public_key,
        )

        return owner_handoff_gate
