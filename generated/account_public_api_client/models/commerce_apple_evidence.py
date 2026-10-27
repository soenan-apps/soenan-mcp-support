from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.commerce_apple_evidence_channel import CommerceAppleEvidenceChannel

T = TypeVar("T", bound="CommerceAppleEvidence")


@_attrs_define
class CommerceAppleEvidence:
    """
    Attributes:
        channel (CommerceAppleEvidenceChannel):
        signed_transaction (str):
    """

    channel: CommerceAppleEvidenceChannel
    signed_transaction: str

    def to_dict(self) -> dict[str, Any]:
        channel = self.channel.value

        signed_transaction = self.signed_transaction

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "channel": channel,
                "signedTransaction": signed_transaction,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        channel = CommerceAppleEvidenceChannel(d.pop("channel"))

        signed_transaction = d.pop("signedTransaction")

        commerce_apple_evidence = cls(
            channel=channel,
            signed_transaction=signed_transaction,
        )

        return commerce_apple_evidence
