from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.e2_ee_owner_key_proof import E2EeOwnerKeyProof
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.e2_ee_envelope import E2EeEnvelope
    from ..models.e2_ee_owner_authority import E2EeOwnerAuthority


T = TypeVar("T", bound="E2EeOwnerRotation")


@_attrs_define
class E2EeOwnerRotation:
    """Project rotations require previous_key_ciphertext; organization rotations must omit it.

    Attributes:
        scope_id (str):
        expected_epoch (int):
        owner_authority (E2EeOwnerAuthority):
        owner_key_proof (E2EeOwnerKeyProof): HPKE Auth uses the selected Owner access-key pair as sender and the
            arteligo.owner-scope-key canonical context, including sender_owner from the signed Owner authority. The device
            still signs the complete original command.
        envelopes (list[E2EeEnvelope]):
        previous_key_ciphertext (str | Unset):
    """

    scope_id: str
    expected_epoch: int
    owner_authority: E2EeOwnerAuthority
    owner_key_proof: E2EeOwnerKeyProof
    envelopes: list[E2EeEnvelope]
    previous_key_ciphertext: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        scope_id = self.scope_id

        expected_epoch = self.expected_epoch

        owner_authority = self.owner_authority.to_dict()

        owner_key_proof = self.owner_key_proof.value

        envelopes = []
        for envelopes_item_data in self.envelopes:
            envelopes_item = envelopes_item_data.to_dict()
            envelopes.append(envelopes_item)

        previous_key_ciphertext = self.previous_key_ciphertext

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "scope_id": scope_id,
                "expected_epoch": expected_epoch,
                "owner_authority": owner_authority,
                "owner_key_proof": owner_key_proof,
                "envelopes": envelopes,
            }
        )
        if previous_key_ciphertext is not UNSET:
            field_dict["previous_key_ciphertext"] = previous_key_ciphertext

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.e2_ee_envelope import E2EeEnvelope
        from ..models.e2_ee_owner_authority import E2EeOwnerAuthority

        d = dict(src_dict)
        scope_id = d.pop("scope_id")

        expected_epoch = d.pop("expected_epoch")

        owner_authority = E2EeOwnerAuthority.from_dict(d.pop("owner_authority"))

        owner_key_proof = E2EeOwnerKeyProof(d.pop("owner_key_proof"))

        envelopes = []
        _envelopes = d.pop("envelopes")
        for envelopes_item_data in _envelopes:
            envelopes_item = E2EeEnvelope.from_dict(envelopes_item_data)

            envelopes.append(envelopes_item)

        previous_key_ciphertext = d.pop("previous_key_ciphertext", UNSET)

        e2_ee_owner_rotation = cls(
            scope_id=scope_id,
            expected_epoch=expected_epoch,
            owner_authority=owner_authority,
            owner_key_proof=owner_key_proof,
            envelopes=envelopes,
            previous_key_ciphertext=previous_key_ciphertext,
        )

        return e2_ee_owner_rotation
