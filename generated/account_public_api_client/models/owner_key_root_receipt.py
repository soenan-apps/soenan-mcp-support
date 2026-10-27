from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.owner_key_root_receipt_outcome import OwnerKeyRootReceiptOutcome
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.owner_authority_head import OwnerAuthorityHead
    from ..models.owner_custody_evidence import OwnerCustodyEvidence


T = TypeVar("T", bound="OwnerKeyRootReceipt")


@_attrs_define
class OwnerKeyRootReceipt:
    """
    Attributes:
        organization_id (str):
        actor_subject (str):
        request_id (str):
        requested_custody_revision (int):
        custody_revision (int):
        outcome (OwnerKeyRootReceiptOutcome):
        revoked_device_ids (list[str]):
        custody_evidence (list[OwnerCustodyEvidence]):
        latest_root_transition (OwnerCustodyEvidence | Unset):
        head (OwnerAuthorityHead | Unset):
    """

    organization_id: str
    actor_subject: str
    request_id: str
    requested_custody_revision: int
    custody_revision: int
    outcome: OwnerKeyRootReceiptOutcome
    revoked_device_ids: list[str]
    custody_evidence: list[OwnerCustodyEvidence]
    latest_root_transition: OwnerCustodyEvidence | Unset = UNSET
    head: OwnerAuthorityHead | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        organization_id = self.organization_id

        actor_subject = self.actor_subject

        request_id = self.request_id

        requested_custody_revision = self.requested_custody_revision

        custody_revision = self.custody_revision

        outcome = self.outcome.value

        revoked_device_ids = self.revoked_device_ids

        custody_evidence = []
        for custody_evidence_item_data in self.custody_evidence:
            custody_evidence_item = custody_evidence_item_data.to_dict()
            custody_evidence.append(custody_evidence_item)

        latest_root_transition: dict[str, Any] | Unset = UNSET
        if not isinstance(self.latest_root_transition, Unset):
            latest_root_transition = self.latest_root_transition.to_dict()

        head: dict[str, Any] | Unset = UNSET
        if not isinstance(self.head, Unset):
            head = self.head.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "organization_id": organization_id,
                "actor_subject": actor_subject,
                "request_id": request_id,
                "requested_custody_revision": requested_custody_revision,
                "custody_revision": custody_revision,
                "outcome": outcome,
                "revoked_device_ids": revoked_device_ids,
                "custody_evidence": custody_evidence,
            }
        )
        if latest_root_transition is not UNSET:
            field_dict["latest_root_transition"] = latest_root_transition
        if head is not UNSET:
            field_dict["head"] = head

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.owner_authority_head import OwnerAuthorityHead
        from ..models.owner_custody_evidence import OwnerCustodyEvidence

        d = dict(src_dict)
        organization_id = d.pop("organization_id")

        actor_subject = d.pop("actor_subject")

        request_id = d.pop("request_id")

        requested_custody_revision = d.pop("requested_custody_revision")

        custody_revision = d.pop("custody_revision")

        outcome = OwnerKeyRootReceiptOutcome(d.pop("outcome"))

        revoked_device_ids = cast(list[str], d.pop("revoked_device_ids"))

        custody_evidence = []
        _custody_evidence = d.pop("custody_evidence")
        for custody_evidence_item_data in _custody_evidence:
            custody_evidence_item = OwnerCustodyEvidence.from_dict(
                custody_evidence_item_data
            )

            custody_evidence.append(custody_evidence_item)

        _latest_root_transition = d.pop("latest_root_transition", UNSET)
        latest_root_transition: OwnerCustodyEvidence | Unset
        if isinstance(_latest_root_transition, Unset):
            latest_root_transition = UNSET
        else:
            latest_root_transition = OwnerCustodyEvidence.from_dict(
                _latest_root_transition
            )

        _head = d.pop("head", UNSET)
        head: OwnerAuthorityHead | Unset
        if isinstance(_head, Unset):
            head = UNSET
        else:
            head = OwnerAuthorityHead.from_dict(_head)

        owner_key_root_receipt = cls(
            organization_id=organization_id,
            actor_subject=actor_subject,
            request_id=request_id,
            requested_custody_revision=requested_custody_revision,
            custody_revision=custody_revision,
            outcome=outcome,
            revoked_device_ids=revoked_device_ids,
            custody_evidence=custody_evidence,
            latest_root_transition=latest_root_transition,
            head=head,
        )

        return owner_key_root_receipt
