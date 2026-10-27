from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.e2_ee_owner_issuer_admission import E2EeOwnerIssuerAdmission


T = TypeVar("T", bound="E2EeOwnerGateRequest")


@_attrs_define
class E2EeOwnerGateRequest:
    """
    Attributes:
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
        issuer_admission (E2EeOwnerIssuerAdmission): The original source-root and exact immutable certificate references
            selected when this command was signed. Later certificates cannot qualify or replace this evidence.
    """

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
    issuer_admission: E2EeOwnerIssuerAdmission

    def to_dict(self) -> dict[str, Any]:
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

        issuer_admission = self.issuer_admission.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
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
                "issuer_admission": issuer_admission,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.e2_ee_owner_issuer_admission import E2EeOwnerIssuerAdmission

        d = dict(src_dict)
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

        issuer_admission = E2EeOwnerIssuerAdmission.from_dict(d.pop("issuer_admission"))

        e2_ee_owner_gate_request = cls(
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
            issuer_admission=issuer_admission,
        )

        return e2_ee_owner_gate_request
