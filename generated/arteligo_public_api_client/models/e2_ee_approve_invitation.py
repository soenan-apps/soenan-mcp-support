from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.e2_ee_owner_key_proof import E2EeOwnerKeyProof
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.e2_ee_envelope import E2EeEnvelope
    from ..models.e2_ee_owner_authority import E2EeOwnerAuthority
    from ..models.e2_ee_signed_command import E2EeSignedCommand


T = TypeVar("T", bound="E2EeApproveInvitation")


@_attrs_define
class E2EeApproveInvitation:
    """
    Attributes:
        request_id (str):
        request_command (E2EeSignedCommand):
        key_epoch (int):
        envelopes (list[E2EeEnvelope]):
        owner_authority (E2EeOwnerAuthority | Unset):
        owner_key_proof (E2EeOwnerKeyProof | Unset): HPKE Auth uses the selected Owner access-key pair as sender and the
            arteligo.owner-scope-key canonical context, including sender_owner from the signed Owner authority. The device
            still signs the complete original command.
    """

    request_id: str
    request_command: E2EeSignedCommand
    key_epoch: int
    envelopes: list[E2EeEnvelope]
    owner_authority: E2EeOwnerAuthority | Unset = UNSET
    owner_key_proof: E2EeOwnerKeyProof | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        request_id = self.request_id

        request_command = self.request_command.to_dict()

        key_epoch = self.key_epoch

        envelopes = []
        for envelopes_item_data in self.envelopes:
            envelopes_item = envelopes_item_data.to_dict()
            envelopes.append(envelopes_item)

        owner_authority: dict[str, Any] | Unset = UNSET
        if not isinstance(self.owner_authority, Unset):
            owner_authority = self.owner_authority.to_dict()

        owner_key_proof: str | Unset = UNSET
        if not isinstance(self.owner_key_proof, Unset):
            owner_key_proof = self.owner_key_proof.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "request_id": request_id,
                "request_command": request_command,
                "key_epoch": key_epoch,
                "envelopes": envelopes,
            }
        )
        if owner_authority is not UNSET:
            field_dict["owner_authority"] = owner_authority
        if owner_key_proof is not UNSET:
            field_dict["owner_key_proof"] = owner_key_proof

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_envelope import E2EeEnvelope
        from ..models.e2_ee_owner_authority import E2EeOwnerAuthority
        from ..models.e2_ee_signed_command import E2EeSignedCommand

        d = dict(src_dict)
        request_id = d.pop("request_id")

        request_command = E2EeSignedCommand.from_dict(d.pop("request_command"))

        key_epoch = d.pop("key_epoch")

        envelopes = []
        _envelopes = d.pop("envelopes")
        for envelopes_item_data in _envelopes:
            envelopes_item = E2EeEnvelope.from_dict(envelopes_item_data)

            envelopes.append(envelopes_item)

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

        e2_ee_approve_invitation = cls(
            request_id=request_id,
            request_command=request_command,
            key_epoch=key_epoch,
            envelopes=envelopes,
            owner_authority=owner_authority,
            owner_key_proof=owner_key_proof,
        )

        return e2_ee_approve_invitation
