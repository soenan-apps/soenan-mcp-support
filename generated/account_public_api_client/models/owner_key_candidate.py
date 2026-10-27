from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="OwnerKeyCandidate")


@_attrs_define
class OwnerKeyCandidate:
    """
    Attributes:
        organization_id (str):
        actor_subject (str):
        candidate_id (str):
        key_id (str):
        public_key (str):
        root_revision (int):
        custody_revision (int):
        offer_digest (str):
        signed_offer (str): Base64url exact signed command bytes.
        identity_anchor_digest (str):
        identity_anchor (str): Base64url exact signed identity anchor bytes.
        recovery_id (str):
        recovery_generation (int):
    """

    organization_id: str
    actor_subject: str
    candidate_id: str
    key_id: str
    public_key: str
    root_revision: int
    custody_revision: int
    offer_digest: str
    signed_offer: str
    identity_anchor_digest: str
    identity_anchor: str
    recovery_id: str
    recovery_generation: int

    def to_dict(self) -> dict[str, Any]:
        organization_id = self.organization_id

        actor_subject = self.actor_subject

        candidate_id = self.candidate_id

        key_id = self.key_id

        public_key = self.public_key

        root_revision = self.root_revision

        custody_revision = self.custody_revision

        offer_digest = self.offer_digest

        signed_offer = self.signed_offer

        identity_anchor_digest = self.identity_anchor_digest

        identity_anchor = self.identity_anchor

        recovery_id = self.recovery_id

        recovery_generation = self.recovery_generation

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "organization_id": organization_id,
                "actor_subject": actor_subject,
                "candidate_id": candidate_id,
                "key_id": key_id,
                "public_key": public_key,
                "root_revision": root_revision,
                "custody_revision": custody_revision,
                "offer_digest": offer_digest,
                "signed_offer": signed_offer,
                "identity_anchor_digest": identity_anchor_digest,
                "identity_anchor": identity_anchor,
                "recovery_id": recovery_id,
                "recovery_generation": recovery_generation,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        organization_id = d.pop("organization_id")

        actor_subject = d.pop("actor_subject")

        candidate_id = d.pop("candidate_id")

        key_id = d.pop("key_id")

        public_key = d.pop("public_key")

        root_revision = d.pop("root_revision")

        custody_revision = d.pop("custody_revision")

        offer_digest = d.pop("offer_digest")

        signed_offer = d.pop("signed_offer")

        identity_anchor_digest = d.pop("identity_anchor_digest")

        identity_anchor = d.pop("identity_anchor")

        recovery_id = d.pop("recovery_id")

        recovery_generation = d.pop("recovery_generation")

        owner_key_candidate = cls(
            organization_id=organization_id,
            actor_subject=actor_subject,
            candidate_id=candidate_id,
            key_id=key_id,
            public_key=public_key,
            root_revision=root_revision,
            custody_revision=custody_revision,
            offer_digest=offer_digest,
            signed_offer=signed_offer,
            identity_anchor_digest=identity_anchor_digest,
            identity_anchor=identity_anchor,
            recovery_id=recovery_id,
            recovery_generation=recovery_generation,
        )

        return owner_key_candidate
