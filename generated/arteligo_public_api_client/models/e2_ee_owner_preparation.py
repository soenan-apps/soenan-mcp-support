from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.e2_ee_owner_authority import E2EeOwnerAuthority
    from ..models.e2_ee_owner_capsule import E2EeOwnerCapsule
    from ..models.e2_ee_owner_gate import E2EeOwnerGate
    from ..models.e2_ee_owner_history_binding import E2EeOwnerHistoryBinding
    from ..models.e2_ee_owner_issuer_admission import E2EeOwnerIssuerAdmission


T = TypeVar("T", bound="E2EeOwnerPreparation")


@_attrs_define
class E2EeOwnerPreparation:
    """
    Attributes:
        organization_id (str):
        preparation_id (str):
        owner_authority (E2EeOwnerAuthority):
        candidate_id (str):
        offer_digest (str):
        source_manifest_id (str):
        source_manifest_digest (str):
        keyring_manifest (list[E2EeOwnerHistoryBinding]):
        gate_descriptor (E2EeOwnerGate):
        capsule (E2EeOwnerCapsule):
        capsule_digest (str):
        issuer_admission (E2EeOwnerIssuerAdmission): The original source-root and exact immutable certificate references
            selected when this command was signed. Later certificates cannot qualify or replace this evidence.
    """

    organization_id: str
    preparation_id: str
    owner_authority: E2EeOwnerAuthority
    candidate_id: str
    offer_digest: str
    source_manifest_id: str
    source_manifest_digest: str
    keyring_manifest: list[E2EeOwnerHistoryBinding]
    gate_descriptor: E2EeOwnerGate
    capsule: E2EeOwnerCapsule
    capsule_digest: str
    issuer_admission: E2EeOwnerIssuerAdmission

    def to_dict(self) -> dict[str, Any]:
        organization_id = self.organization_id

        preparation_id = self.preparation_id

        owner_authority = self.owner_authority.to_dict()

        candidate_id = self.candidate_id

        offer_digest = self.offer_digest

        source_manifest_id = self.source_manifest_id

        source_manifest_digest = self.source_manifest_digest

        keyring_manifest = []
        for keyring_manifest_item_data in self.keyring_manifest:
            keyring_manifest_item = keyring_manifest_item_data.to_dict()
            keyring_manifest.append(keyring_manifest_item)

        gate_descriptor = self.gate_descriptor.to_dict()

        capsule = self.capsule.to_dict()

        capsule_digest = self.capsule_digest

        issuer_admission = self.issuer_admission.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "organization_id": organization_id,
                "preparation_id": preparation_id,
                "owner_authority": owner_authority,
                "candidate_id": candidate_id,
                "offer_digest": offer_digest,
                "source_manifest_id": source_manifest_id,
                "source_manifest_digest": source_manifest_digest,
                "keyring_manifest": keyring_manifest,
                "gate_descriptor": gate_descriptor,
                "capsule": capsule,
                "capsule_digest": capsule_digest,
                "issuer_admission": issuer_admission,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_owner_authority import E2EeOwnerAuthority
        from ..models.e2_ee_owner_capsule import E2EeOwnerCapsule
        from ..models.e2_ee_owner_gate import E2EeOwnerGate
        from ..models.e2_ee_owner_history_binding import E2EeOwnerHistoryBinding
        from ..models.e2_ee_owner_issuer_admission import E2EeOwnerIssuerAdmission

        d = dict(src_dict)
        organization_id = d.pop("organization_id")

        preparation_id = d.pop("preparation_id")

        owner_authority = E2EeOwnerAuthority.from_dict(d.pop("owner_authority"))

        candidate_id = d.pop("candidate_id")

        offer_digest = d.pop("offer_digest")

        source_manifest_id = d.pop("source_manifest_id")

        source_manifest_digest = d.pop("source_manifest_digest")

        keyring_manifest = []
        _keyring_manifest = d.pop("keyring_manifest")
        for keyring_manifest_item_data in _keyring_manifest:
            keyring_manifest_item = E2EeOwnerHistoryBinding.from_dict(
                keyring_manifest_item_data
            )

            keyring_manifest.append(keyring_manifest_item)

        gate_descriptor = E2EeOwnerGate.from_dict(d.pop("gate_descriptor"))

        capsule = E2EeOwnerCapsule.from_dict(d.pop("capsule"))

        capsule_digest = d.pop("capsule_digest")

        issuer_admission = E2EeOwnerIssuerAdmission.from_dict(d.pop("issuer_admission"))

        e2_ee_owner_preparation = cls(
            organization_id=organization_id,
            preparation_id=preparation_id,
            owner_authority=owner_authority,
            candidate_id=candidate_id,
            offer_digest=offer_digest,
            source_manifest_id=source_manifest_id,
            source_manifest_digest=source_manifest_digest,
            keyring_manifest=keyring_manifest,
            gate_descriptor=gate_descriptor,
            capsule=capsule,
            capsule_digest=capsule_digest,
            issuer_admission=issuer_admission,
        )

        return e2_ee_owner_preparation
