from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.e2_ee_owner_key_proof import E2EeOwnerKeyProof
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.e2_ee_envelope import E2EeEnvelope
    from ..models.e2_ee_organization_participation import E2EeOrganizationParticipation
    from ..models.e2_ee_owner_authority import E2EeOwnerAuthority
    from ..models.e2_ee_owner_issuer_admission import E2EeOwnerIssuerAdmission


T = TypeVar("T", bound="E2EeOrganizationAdmission")


@_attrs_define
class E2EeOrganizationAdmission:
    """
    Attributes:
        scope_id (str):
        key_epoch (int):
        envelopes (list[E2EeEnvelope]):
        participation (E2EeOrganizationParticipation):
        owner_authority (E2EeOwnerAuthority | Unset):
        owner_key_proof (E2EeOwnerKeyProof | Unset): HPKE Auth uses the selected Owner access-key pair as sender and the
            arteligo.owner-scope-key canonical context, including sender_owner from the signed Owner authority. The device
            still signs the complete original command.
        issuer_admission (E2EeOwnerIssuerAdmission | Unset): The original source-root and exact immutable certificate
            references selected when this command was signed. Later certificates cannot qualify or replace this evidence.
    """

    scope_id: str
    key_epoch: int
    envelopes: list[E2EeEnvelope]
    participation: E2EeOrganizationParticipation
    owner_authority: E2EeOwnerAuthority | Unset = UNSET
    owner_key_proof: E2EeOwnerKeyProof | Unset = UNSET
    issuer_admission: E2EeOwnerIssuerAdmission | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        scope_id = self.scope_id

        key_epoch = self.key_epoch

        envelopes = []
        for envelopes_item_data in self.envelopes:
            envelopes_item = envelopes_item_data.to_dict()
            envelopes.append(envelopes_item)

        participation = self.participation.to_dict()

        owner_authority: dict[str, Any] | Unset = UNSET
        if not isinstance(self.owner_authority, Unset):
            owner_authority = self.owner_authority.to_dict()

        owner_key_proof: str | Unset = UNSET
        if not isinstance(self.owner_key_proof, Unset):
            owner_key_proof = self.owner_key_proof.value

        issuer_admission: dict[str, Any] | Unset = UNSET
        if not isinstance(self.issuer_admission, Unset):
            issuer_admission = self.issuer_admission.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "scope_id": scope_id,
                "key_epoch": key_epoch,
                "envelopes": envelopes,
                "participation": participation,
            }
        )
        if owner_authority is not UNSET:
            field_dict["owner_authority"] = owner_authority
        if owner_key_proof is not UNSET:
            field_dict["owner_key_proof"] = owner_key_proof
        if issuer_admission is not UNSET:
            field_dict["issuer_admission"] = issuer_admission

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.e2_ee_envelope import E2EeEnvelope
        from ..models.e2_ee_organization_participation import (
            E2EeOrganizationParticipation,
        )
        from ..models.e2_ee_owner_authority import E2EeOwnerAuthority
        from ..models.e2_ee_owner_issuer_admission import E2EeOwnerIssuerAdmission

        d = dict(src_dict)
        scope_id = d.pop("scope_id")

        key_epoch = d.pop("key_epoch")

        envelopes = []
        _envelopes = d.pop("envelopes")
        for envelopes_item_data in _envelopes:
            envelopes_item = E2EeEnvelope.from_dict(envelopes_item_data)

            envelopes.append(envelopes_item)

        participation = E2EeOrganizationParticipation.from_dict(d.pop("participation"))

        _owner_authority = d.pop("owner_authority", UNSET)
        owner_authority: E2EeOwnerAuthority | Unset
        if isinstance(_owner_authority, Unset):
            owner_authority = UNSET
        else:
            owner_authority = E2EeOwnerAuthority.from_dict(_owner_authority)

        _owner_key_proof = d.pop("owner_key_proof", UNSET)
        owner_key_proof: E2EeOwnerKeyProof | Unset
        if isinstance(_owner_key_proof, Unset):
            owner_key_proof = UNSET
        else:
            owner_key_proof = E2EeOwnerKeyProof(_owner_key_proof)

        _issuer_admission = d.pop("issuer_admission", UNSET)
        issuer_admission: E2EeOwnerIssuerAdmission | Unset
        if isinstance(_issuer_admission, Unset):
            issuer_admission = UNSET
        else:
            issuer_admission = E2EeOwnerIssuerAdmission.from_dict(_issuer_admission)

        e2_ee_organization_admission = cls(
            scope_id=scope_id,
            key_epoch=key_epoch,
            envelopes=envelopes,
            participation=participation,
            owner_authority=owner_authority,
            owner_key_proof=owner_key_proof,
            issuer_admission=issuer_admission,
        )

        return e2_ee_organization_admission
