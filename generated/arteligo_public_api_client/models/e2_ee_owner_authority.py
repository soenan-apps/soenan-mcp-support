from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.e2_ee_owner_authority_state import E2EeOwnerAuthorityState

T = TypeVar("T", bound="E2EeOwnerAuthority")


@_attrs_define
class E2EeOwnerAuthority:
    """
    Attributes:
        organization_id (str):
        ownership_revision (int):
        owner_subject (str):
        key_id (str):
        key_epoch (int):
        public_key (str):
        binding_digest (str):
        state (E2EeOwnerAuthorityState):
        read_capability (str):
    """

    organization_id: str
    ownership_revision: int
    owner_subject: str
    key_id: str
    key_epoch: int
    public_key: str
    binding_digest: str
    state: E2EeOwnerAuthorityState
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

        state = E2EeOwnerAuthorityState(d.pop("state"))

        read_capability = d.pop("read_capability")

        e2_ee_owner_authority = cls(
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

        return e2_ee_owner_authority
