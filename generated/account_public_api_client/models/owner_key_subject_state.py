from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.owner_key_dependency_outcome import OwnerKeyDependencyOutcome
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.owner_custody_evidence import OwnerCustodyEvidence


T = TypeVar("T", bound="OwnerKeySubjectState")


@_attrs_define
class OwnerKeySubjectState:
    """Repeated frames for the same account_subject concatenate revoked_device_ids. All other fields agree. The enclosing
    complete marker closes the subject state.

        Attributes:
            account_subject (str):
            outcome (OwnerKeyDependencyOutcome):
            custody_revision (int):
            revoked_device_ids (list[str]):
            owner_bindings_digest (str):
            latest_root_transition (OwnerCustodyEvidence | Unset):
    """

    account_subject: str
    outcome: OwnerKeyDependencyOutcome
    custody_revision: int
    revoked_device_ids: list[str]
    owner_bindings_digest: str
    latest_root_transition: OwnerCustodyEvidence | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        account_subject = self.account_subject

        outcome = self.outcome.value

        custody_revision = self.custody_revision

        revoked_device_ids = self.revoked_device_ids

        owner_bindings_digest = self.owner_bindings_digest

        latest_root_transition: dict[str, Any] | Unset = UNSET
        if not isinstance(self.latest_root_transition, Unset):
            latest_root_transition = self.latest_root_transition.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "account_subject": account_subject,
                "outcome": outcome,
                "custody_revision": custody_revision,
                "revoked_device_ids": revoked_device_ids,
                "owner_bindings_digest": owner_bindings_digest,
            }
        )
        if latest_root_transition is not UNSET:
            field_dict["latest_root_transition"] = latest_root_transition

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.owner_custody_evidence import OwnerCustodyEvidence

        d = dict(src_dict)
        account_subject = d.pop("account_subject")

        outcome = OwnerKeyDependencyOutcome(d.pop("outcome"))

        custody_revision = d.pop("custody_revision")

        revoked_device_ids = cast(list[str], d.pop("revoked_device_ids"))

        owner_bindings_digest = d.pop("owner_bindings_digest")

        _latest_root_transition = d.pop("latest_root_transition", UNSET)
        latest_root_transition: OwnerCustodyEvidence | Unset
        if isinstance(_latest_root_transition, Unset):
            latest_root_transition = UNSET
        else:
            latest_root_transition = OwnerCustodyEvidence.from_dict(
                _latest_root_transition
            )

        owner_key_subject_state = cls(
            account_subject=account_subject,
            outcome=outcome,
            custody_revision=custody_revision,
            revoked_device_ids=revoked_device_ids,
            owner_bindings_digest=owner_bindings_digest,
            latest_root_transition=latest_root_transition,
        )

        return owner_key_subject_state
