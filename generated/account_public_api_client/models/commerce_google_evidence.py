from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.commerce_google_evidence_channel import CommerceGoogleEvidenceChannel
from ..models.commerce_purchase_kind import CommercePurchaseKind

T = TypeVar("T", bound="CommerceGoogleEvidence")


@_attrs_define
class CommerceGoogleEvidence:
    """
    Attributes:
        channel (CommerceGoogleEvidenceChannel):
        package_id (str):
        purchase_token (str):
        purchase_kind (CommercePurchaseKind):
    """

    channel: CommerceGoogleEvidenceChannel
    package_id: str
    purchase_token: str
    purchase_kind: CommercePurchaseKind

    def to_dict(self) -> dict[str, Any]:
        channel = self.channel.value

        package_id = self.package_id

        purchase_token = self.purchase_token

        purchase_kind = self.purchase_kind.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "channel": channel,
                "packageId": package_id,
                "purchaseToken": purchase_token,
                "purchaseKind": purchase_kind,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        channel = CommerceGoogleEvidenceChannel(d.pop("channel"))

        package_id = d.pop("packageId")

        purchase_token = d.pop("purchaseToken")

        purchase_kind = CommercePurchaseKind(d.pop("purchaseKind"))

        commerce_google_evidence = cls(
            channel=channel,
            package_id=package_id,
            purchase_token=purchase_token,
            purchase_kind=purchase_kind,
        )

        return commerce_google_evidence
