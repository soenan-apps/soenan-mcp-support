from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.commerce_apple_evidence import CommerceAppleEvidence
    from ..models.commerce_google_evidence import CommerceGoogleEvidence
    from ..models.commerce_stripe_evidence import CommerceStripeEvidence


T = TypeVar("T", bound="CommerceVerifyRequest")


@_attrs_define
class CommerceVerifyRequest:
    """
    Attributes:
        evidence (CommerceAppleEvidence | CommerceGoogleEvidence | CommerceStripeEvidence):
        attempt_id (UUID | Unset):
    """

    evidence: CommerceAppleEvidence | CommerceGoogleEvidence | CommerceStripeEvidence
    attempt_id: UUID | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        from ..models.commerce_apple_evidence import CommerceAppleEvidence
        from ..models.commerce_google_evidence import CommerceGoogleEvidence

        evidence: dict[str, Any]
        if isinstance(self.evidence, CommerceAppleEvidence):
            evidence = self.evidence.to_dict()
        elif isinstance(self.evidence, CommerceGoogleEvidence):
            evidence = self.evidence.to_dict()
        else:
            evidence = self.evidence.to_dict()

        attempt_id: str | Unset = UNSET
        if not isinstance(self.attempt_id, Unset):
            attempt_id = str(self.attempt_id)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "evidence": evidence,
            }
        )
        if attempt_id is not UNSET:
            field_dict["attemptId"] = attempt_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.commerce_apple_evidence import CommerceAppleEvidence
        from ..models.commerce_google_evidence import CommerceGoogleEvidence
        from ..models.commerce_stripe_evidence import CommerceStripeEvidence

        d = dict(src_dict)

        def _parse_evidence(
            data: object,
        ) -> CommerceAppleEvidence | CommerceGoogleEvidence | CommerceStripeEvidence:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_commerce_evidence_type_0 = (
                    CommerceAppleEvidence.from_dict(data)
                )

                return componentsschemas_commerce_evidence_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_commerce_evidence_type_1 = (
                    CommerceGoogleEvidence.from_dict(data)
                )

                return componentsschemas_commerce_evidence_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_commerce_evidence_type_2 = (
                CommerceStripeEvidence.from_dict(data)
            )

            return componentsschemas_commerce_evidence_type_2

        evidence = _parse_evidence(d.pop("evidence"))

        _attempt_id = d.pop("attemptId", UNSET)
        attempt_id: UUID | Unset
        if isinstance(_attempt_id, Unset):
            attempt_id = UNSET
        else:
            attempt_id = UUID(_attempt_id)

        commerce_verify_request = cls(
            evidence=evidence,
            attempt_id=attempt_id,
        )

        return commerce_verify_request
