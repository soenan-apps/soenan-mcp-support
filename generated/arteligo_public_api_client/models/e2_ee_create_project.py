from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.e2_ee_owner_key_proof import E2EeOwnerKeyProof
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.e2_ee_content_record_write import E2EeContentRecordWrite
    from ..models.e2_ee_envelope import E2EeEnvelope
    from ..models.e2_ee_owner_authority import E2EeOwnerAuthority


T = TypeVar("T", bound="E2EeCreateProject")


@_attrs_define
class E2EeCreateProject:
    r"""
    Attributes:
        project_id (str): New clients default to prj_<commitment>_<suffix>, a 101-character ID with a 64-character
            lowercase hexadecimal SHA-256 commitment and a 32-character lowercase hexadecimal random suffix. The commitment
            hashes UTF-8 "arteligo-project-creator-v1\n" followed by the raw 32-byte Ed25519 creator signing public key.
            Existing opaque IDs, including prj_ followed by 32 lowercase hexadecimal characters, remain unchanged and valid,
            including in saved signed commands and receipt replay. The commitment is client-side evidence of the creator
            signing key only. It does not establish an account, root, current head, organization or ownership, and the
            server must not derive authorization from the ID format.
        owner_org (str):
        participation_policy (str):
        envelopes (list[E2EeEnvelope]):
        records (list[E2EeContentRecordWrite]):
        owner_authority (E2EeOwnerAuthority | Unset):
        owner_key_proof (E2EeOwnerKeyProof | Unset): HPKE Auth uses the selected Owner access-key pair as sender and the
            arteligo.owner-scope-key canonical context, including sender_owner from the signed Owner authority. The device
            still signs the complete original command.
    """

    project_id: str
    owner_org: str
    participation_policy: str
    envelopes: list[E2EeEnvelope]
    records: list[E2EeContentRecordWrite]
    owner_authority: E2EeOwnerAuthority | Unset = UNSET
    owner_key_proof: E2EeOwnerKeyProof | Unset = UNSET

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

        owner_authority: dict[str, Any] | Unset = UNSET
        if not isinstance(self.owner_authority, Unset):
            owner_authority = self.owner_authority.to_dict()

        owner_key_proof: str | Unset = UNSET
        if not isinstance(self.owner_key_proof, Unset):
            owner_key_proof = self.owner_key_proof.value

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
        if owner_authority is not UNSET:
            field_dict["owner_authority"] = owner_authority
        if owner_key_proof is not UNSET:
            field_dict["owner_key_proof"] = owner_key_proof

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_content_record_write import E2EeContentRecordWrite
        from ..models.e2_ee_envelope import E2EeEnvelope
        from ..models.e2_ee_owner_authority import E2EeOwnerAuthority

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
            records_item = E2EeContentRecordWrite.from_dict(records_item_data)

            records.append(records_item)

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

        e2_ee_create_project = cls(
            project_id=project_id,
            owner_org=owner_org,
            participation_policy=participation_policy,
            envelopes=envelopes,
            records=records,
            owner_authority=owner_authority,
            owner_key_proof=owner_key_proof,
        )

        return e2_ee_create_project
