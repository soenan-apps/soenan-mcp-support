from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.owner_transfer_blocker import OwnerTransferBlocker
from ..models.owner_transfer_decision_state import OwnerTransferDecisionState
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.owner_authority_head import OwnerAuthorityHead


T = TypeVar("T", bound="OwnerTransferDecision")


@_attrs_define
class OwnerTransferDecision:
    """The exact durable ownership decision. Binding, candidate-offer, source-manifest, and preparation digests use the
    full signed-command commitment described by OwnerAuthorityHead.binding_digest, with their respective operation name.
    History-manifest digests hash canonical JSON.

        Attributes:
            organization_id (str):
            operation_id (str):
            actor_subject (str):
            target_subject (str):
            expected_ownership_revision (int):
            state (OwnerTransferDecisionState):
            reservation_id (str):
            coverage_digest (str):
            preparation_id (str):
            preparation_digest (str):
            source_manifest_id (str):
            source_manifest_digest (str):
            candidate_id (str):
            candidate_offer_digest (str):
            gate_id (str):
            history_manifest_digest (str):
            no_content (bool):
            blocker (OwnerTransferBlocker):
            head (OwnerAuthorityHead | Unset):
    """

    organization_id: str
    operation_id: str
    actor_subject: str
    target_subject: str
    expected_ownership_revision: int
    state: OwnerTransferDecisionState
    reservation_id: str
    coverage_digest: str
    preparation_id: str
    preparation_digest: str
    source_manifest_id: str
    source_manifest_digest: str
    candidate_id: str
    candidate_offer_digest: str
    gate_id: str
    history_manifest_digest: str
    no_content: bool
    blocker: OwnerTransferBlocker
    head: OwnerAuthorityHead | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        organization_id = self.organization_id

        operation_id = self.operation_id

        actor_subject = self.actor_subject

        target_subject = self.target_subject

        expected_ownership_revision = self.expected_ownership_revision

        state = self.state.value

        reservation_id = self.reservation_id

        coverage_digest = self.coverage_digest

        preparation_id = self.preparation_id

        preparation_digest = self.preparation_digest

        source_manifest_id = self.source_manifest_id

        source_manifest_digest = self.source_manifest_digest

        candidate_id = self.candidate_id

        candidate_offer_digest = self.candidate_offer_digest

        gate_id = self.gate_id

        history_manifest_digest = self.history_manifest_digest

        no_content = self.no_content

        blocker = self.blocker.value

        head: dict[str, Any] | Unset = UNSET
        if not isinstance(self.head, Unset):
            head = self.head.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "organization_id": organization_id,
                "operation_id": operation_id,
                "actor_subject": actor_subject,
                "target_subject": target_subject,
                "expected_ownership_revision": expected_ownership_revision,
                "state": state,
                "reservation_id": reservation_id,
                "coverage_digest": coverage_digest,
                "preparation_id": preparation_id,
                "preparation_digest": preparation_digest,
                "source_manifest_id": source_manifest_id,
                "source_manifest_digest": source_manifest_digest,
                "candidate_id": candidate_id,
                "candidate_offer_digest": candidate_offer_digest,
                "gate_id": gate_id,
                "history_manifest_digest": history_manifest_digest,
                "no_content": no_content,
                "blocker": blocker,
            }
        )
        if head is not UNSET:
            field_dict["head"] = head

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.owner_authority_head import OwnerAuthorityHead

        d = dict(src_dict)
        organization_id = d.pop("organization_id")

        operation_id = d.pop("operation_id")

        actor_subject = d.pop("actor_subject")

        target_subject = d.pop("target_subject")

        expected_ownership_revision = d.pop("expected_ownership_revision")

        state = OwnerTransferDecisionState(d.pop("state"))

        reservation_id = d.pop("reservation_id")

        coverage_digest = d.pop("coverage_digest")

        preparation_id = d.pop("preparation_id")

        preparation_digest = d.pop("preparation_digest")

        source_manifest_id = d.pop("source_manifest_id")

        source_manifest_digest = d.pop("source_manifest_digest")

        candidate_id = d.pop("candidate_id")

        candidate_offer_digest = d.pop("candidate_offer_digest")

        gate_id = d.pop("gate_id")

        history_manifest_digest = d.pop("history_manifest_digest")

        no_content = d.pop("no_content")

        blocker = OwnerTransferBlocker(d.pop("blocker"))

        _head = d.pop("head", UNSET)
        head: OwnerAuthorityHead | Unset
        if isinstance(_head, Unset):
            head = UNSET
        else:
            head = OwnerAuthorityHead.from_dict(_head)

        owner_transfer_decision = cls(
            organization_id=organization_id,
            operation_id=operation_id,
            actor_subject=actor_subject,
            target_subject=target_subject,
            expected_ownership_revision=expected_ownership_revision,
            state=state,
            reservation_id=reservation_id,
            coverage_digest=coverage_digest,
            preparation_id=preparation_id,
            preparation_digest=preparation_digest,
            source_manifest_id=source_manifest_id,
            source_manifest_digest=source_manifest_digest,
            candidate_id=candidate_id,
            candidate_offer_digest=candidate_offer_digest,
            gate_id=gate_id,
            history_manifest_digest=history_manifest_digest,
            no_content=no_content,
            blocker=blocker,
            head=head,
        )

        return owner_transfer_decision
