from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.commerce_stripe_evidence_channel import CommerceStripeEvidenceChannel

T = TypeVar("T", bound="CommerceStripeEvidence")


@_attrs_define
class CommerceStripeEvidence:
    """
    Attributes:
        channel (CommerceStripeEvidenceChannel):
        checkout_session_id (str):
    """

    channel: CommerceStripeEvidenceChannel
    checkout_session_id: str

    def to_dict(self) -> dict[str, Any]:
        channel = self.channel.value

        checkout_session_id = self.checkout_session_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "channel": channel,
                "checkoutSessionId": checkout_session_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        channel = CommerceStripeEvidenceChannel(d.pop("channel"))

        checkout_session_id = d.pop("checkoutSessionId")

        commerce_stripe_evidence = cls(
            channel=channel,
            checkout_session_id=checkout_session_id,
        )

        return commerce_stripe_evidence
