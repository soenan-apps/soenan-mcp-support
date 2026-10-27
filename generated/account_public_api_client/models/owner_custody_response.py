from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.owner_authority_head import OwnerAuthorityHead
    from ..models.owner_custody_evidence import OwnerCustodyEvidence


T = TypeVar("T", bound="OwnerCustodyResponse")


@_attrs_define
class OwnerCustodyResponse:
    """
    Attributes:
        challenge (str):
        organization_id (str):
        account_subject (str):
        custody_revision (int):
        owner_bindings_digest (str): Unpadded base64url SHA-256 of JCS of ALL immutable Account-selected bindings whose
            original owner_subject is this account_subject, including retired historical selections. Array elements contain
            only organization_id and binding_digest, sorted ascending by organization_id then binding_digest in UTF-8 byte
            order. Root replacement must hash the own selections actually included in its recoverable history and match this
            fresh observation; copying the observed hash without including those secrets is invalid.
        revoked_device_ids (list[str]): Subject-wide monotonic negatives, never an approved-device directory.
        can_manage_organization_keys (bool): Current active built-in Owner or Admin organization membership, not
            cryptographic identity or product entitlement.
        can_receive_organization_keys (bool): Current active organization membership of any role, including viewer, with
            an active organization and non-disabled account. False for removed or suspended members. This is a membership
            permission fact, not cryptographic identity or product entitlement.
        head (OwnerAuthorityHead):
        evidence (OwnerCustodyEvidence | Unset):
        latest_root_transition (OwnerCustodyEvidence | Unset):
    """

    challenge: str
    organization_id: str
    account_subject: str
    custody_revision: int
    owner_bindings_digest: str
    revoked_device_ids: list[str]
    can_manage_organization_keys: bool
    can_receive_organization_keys: bool
    head: OwnerAuthorityHead
    evidence: OwnerCustodyEvidence | Unset = UNSET
    latest_root_transition: OwnerCustodyEvidence | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        challenge = self.challenge

        organization_id = self.organization_id

        account_subject = self.account_subject

        custody_revision = self.custody_revision

        owner_bindings_digest = self.owner_bindings_digest

        revoked_device_ids = self.revoked_device_ids

        can_manage_organization_keys = self.can_manage_organization_keys

        can_receive_organization_keys = self.can_receive_organization_keys

        head = self.head.to_dict()

        evidence: dict[str, Any] | Unset = UNSET
        if not isinstance(self.evidence, Unset):
            evidence = self.evidence.to_dict()

        latest_root_transition: dict[str, Any] | Unset = UNSET
        if not isinstance(self.latest_root_transition, Unset):
            latest_root_transition = self.latest_root_transition.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "challenge": challenge,
                "organization_id": organization_id,
                "account_subject": account_subject,
                "custody_revision": custody_revision,
                "owner_bindings_digest": owner_bindings_digest,
                "revoked_device_ids": revoked_device_ids,
                "can_manage_organization_keys": can_manage_organization_keys,
                "can_receive_organization_keys": can_receive_organization_keys,
                "head": head,
            }
        )
        if evidence is not UNSET:
            field_dict["evidence"] = evidence
        if latest_root_transition is not UNSET:
            field_dict["latest_root_transition"] = latest_root_transition

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.owner_authority_head import OwnerAuthorityHead
        from ..models.owner_custody_evidence import OwnerCustodyEvidence

        d = dict(src_dict)
        challenge = d.pop("challenge")

        organization_id = d.pop("organization_id")

        account_subject = d.pop("account_subject")

        custody_revision = d.pop("custody_revision")

        owner_bindings_digest = d.pop("owner_bindings_digest")

        revoked_device_ids = cast(list[str], d.pop("revoked_device_ids"))

        can_manage_organization_keys = d.pop("can_manage_organization_keys")

        can_receive_organization_keys = d.pop("can_receive_organization_keys")

        head = OwnerAuthorityHead.from_dict(d.pop("head"))

        _evidence = d.pop("evidence", UNSET)
        evidence: OwnerCustodyEvidence | Unset
        if isinstance(_evidence, Unset):
            evidence = UNSET
        else:
            evidence = OwnerCustodyEvidence.from_dict(_evidence)

        _latest_root_transition = d.pop("latest_root_transition", UNSET)
        latest_root_transition: OwnerCustodyEvidence | Unset
        if isinstance(_latest_root_transition, Unset):
            latest_root_transition = UNSET
        else:
            latest_root_transition = OwnerCustodyEvidence.from_dict(
                _latest_root_transition
            )

        owner_custody_response = cls(
            challenge=challenge,
            organization_id=organization_id,
            account_subject=account_subject,
            custody_revision=custody_revision,
            owner_bindings_digest=owner_bindings_digest,
            revoked_device_ids=revoked_device_ids,
            can_manage_organization_keys=can_manage_organization_keys,
            can_receive_organization_keys=can_receive_organization_keys,
            head=head,
            evidence=evidence,
            latest_root_transition=latest_root_transition,
        )

        return owner_custody_response
