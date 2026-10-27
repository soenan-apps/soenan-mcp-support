from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.owner_authority_head_state import OwnerAuthorityHeadState

T = TypeVar("T", bound="OwnerAuthorityHead")


@_attrs_define
class OwnerAuthorityHead:
    r"""
    Attributes:
        organization_id (str):
        ownership_revision (int):
        owner_subject (str):
        key_id (str):
        key_epoch (int): Monotonic across registrations and transfers, including unprovisioned no-content successors.
        public_key (str):
        binding_digest (str): Unpadded base64url SHA-256 of UTF8("arteligo-owner-evidence-v1\n" + operation + "\n")
            followed by JCS({device_id, body_bytes, signature}). The original body_bytes string is retained without re-
            encoding its body.
        state (OwnerAuthorityHeadState):
        read_capability (str):
    """

    organization_id: str
    ownership_revision: int
    owner_subject: str
    key_id: str
    key_epoch: int
    public_key: str
    binding_digest: str
    state: OwnerAuthorityHeadState
    read_capability: str

    def to_dict(self) -> dict[str, Any]:
        organization_id = self.organization_id

        ownership_revision = self.ownership_revision

        owner_subject = self.owner_subject

        key_id = self.key_id

        key_epoch = self.key_epoch

        public_key = self.public_key

        binding_digest = self.binding_digest

        state = self.state.value

        read_capability = self.read_capability

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "organization_id": organization_id,
                "ownership_revision": ownership_revision,
                "owner_subject": owner_subject,
                "key_id": key_id,
                "key_epoch": key_epoch,
                "public_key": public_key,
                "binding_digest": binding_digest,
                "state": state,
                "read_capability": read_capability,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        organization_id = d.pop("organization_id")

        ownership_revision = d.pop("ownership_revision")

        owner_subject = d.pop("owner_subject")

        key_id = d.pop("key_id")

        key_epoch = d.pop("key_epoch")

        public_key = d.pop("public_key")

        binding_digest = d.pop("binding_digest")

        state = OwnerAuthorityHeadState(d.pop("state"))

        read_capability = d.pop("read_capability")

        owner_authority_head = cls(
            organization_id=organization_id,
            ownership_revision=ownership_revision,
            owner_subject=owner_subject,
            key_id=key_id,
            key_epoch=key_epoch,
            public_key=public_key,
            binding_digest=binding_digest,
            state=state,
            read_capability=read_capability,
        )

        return owner_authority_head
