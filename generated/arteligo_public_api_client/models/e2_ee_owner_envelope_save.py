from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.e2_ee_owner_key_proof import E2EeOwnerKeyProof

if TYPE_CHECKING:
    from ..models.e2_ee_envelope import E2EeEnvelope
    from ..models.e2_ee_owner_authority import E2EeOwnerAuthority


T = TypeVar("T", bound="E2EeOwnerEnvelopeSave")


@_attrs_define
class E2EeOwnerEnvelopeSave:
    """
    Attributes:
        scope_id (str):
        key_epoch (int):
        owner_authority (E2EeOwnerAuthority):
        owner_key_proof (E2EeOwnerKeyProof): HPKE Auth uses the selected Owner access-key pair as sender and the
            arteligo.owner-scope-key canonical context, including sender_owner from the signed Owner authority. The device
            still signs the complete original command.
        envelopes (list[E2EeEnvelope]):
    """

    scope_id: str
    key_epoch: int
    owner_authority: E2EeOwnerAuthority
    owner_key_proof: E2EeOwnerKeyProof
    envelopes: list[E2EeEnvelope]

    def to_dict(self) -> dict[str, Any]:
        scope_id = self.scope_id

        key_epoch = self.key_epoch

        owner_authority = self.owner_authority.to_dict()

        owner_key_proof = self.owner_key_proof.value

        envelopes = []
        for envelopes_item_data in self.envelopes:
            envelopes_item = envelopes_item_data.to_dict()
            envelopes.append(envelopes_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "scope_id": scope_id,
                "key_epoch": key_epoch,
                "owner_authority": owner_authority,
                "owner_key_proof": owner_key_proof,
                "envelopes": envelopes,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.e2_ee_envelope import E2EeEnvelope
        from ..models.e2_ee_owner_authority import E2EeOwnerAuthority

        d = dict(src_dict)
        scope_id = d.pop("scope_id")

        key_epoch = d.pop("key_epoch")

        owner_authority = E2EeOwnerAuthority.from_dict(d.pop("owner_authority"))

        owner_key_proof = E2EeOwnerKeyProof(d.pop("owner_key_proof"))

        envelopes = []
        _envelopes = d.pop("envelopes")
        for envelopes_item_data in _envelopes:
            envelopes_item = E2EeEnvelope.from_dict(envelopes_item_data)

            envelopes.append(envelopes_item)

        e2_ee_owner_envelope_save = cls(
            scope_id=scope_id,
            key_epoch=key_epoch,
            owner_authority=owner_authority,
            owner_key_proof=owner_key_proof,
            envelopes=envelopes,
        )

        return e2_ee_owner_envelope_save
