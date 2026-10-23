from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.owner_custody_evidence import OwnerCustodyEvidence


T = TypeVar("T", bound="OwnerCustodyEvidenceResponse")


@_attrs_define
class OwnerCustodyEvidenceResponse:
    """
    Attributes:
        challenge (str):
        evidence (OwnerCustodyEvidence):
    """

    challenge: str
    evidence: OwnerCustodyEvidence

    def to_dict(self) -> dict[str, Any]:
        challenge = self.challenge

        evidence = self.evidence.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "challenge": challenge,
                "evidence": evidence,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.owner_custody_evidence import OwnerCustodyEvidence

        d = dict(src_dict)
        challenge = d.pop("challenge")

        evidence = OwnerCustodyEvidence.from_dict(d.pop("evidence"))

        owner_custody_evidence_response = cls(
            challenge=challenge,
            evidence=evidence,
        )

        return owner_custody_evidence_response
