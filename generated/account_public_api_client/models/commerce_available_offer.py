from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.commerce_channel import CommerceChannel
from ..models.commerce_purchase_kind import CommercePurchaseKind
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.commerce_right import CommerceRight


T = TypeVar("T", bound="CommerceAvailableOffer")


@_attrs_define
class CommerceAvailableOffer:
    """
    Attributes:
        offer_version (str):
        contract_target_id (str):
        purchase_kind (CommercePurchaseKind):
        channels (list[CommerceChannel]):
        rights (list[CommerceRight]):
        name (str | Unset):
        description (str | Unset):
    """

    offer_version: str
    contract_target_id: str
    purchase_kind: CommercePurchaseKind
    channels: list[CommerceChannel]
    rights: list[CommerceRight]
    name: str | Unset = UNSET
    description: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        offer_version = self.offer_version

        contract_target_id = self.contract_target_id

        purchase_kind = self.purchase_kind.value

        channels = []
        for channels_item_data in self.channels:
            channels_item = channels_item_data.value
            channels.append(channels_item)

        rights = []
        for rights_item_data in self.rights:
            rights_item = rights_item_data.to_dict()
            rights.append(rights_item)

        name = self.name

        description = self.description

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "offerVersion": offer_version,
                "contractTargetId": contract_target_id,
                "purchaseKind": purchase_kind,
                "channels": channels,
                "rights": rights,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.commerce_right import CommerceRight

        d = dict(src_dict)
        offer_version = d.pop("offerVersion")

        contract_target_id = d.pop("contractTargetId")

        purchase_kind = CommercePurchaseKind(d.pop("purchaseKind"))

        channels = []
        _channels = d.pop("channels")
        for channels_item_data in _channels:
            channels_item = CommerceChannel(channels_item_data)

            channels.append(channels_item)

        rights = []
        _rights = d.pop("rights")
        for rights_item_data in _rights:
            rights_item = CommerceRight.from_dict(rights_item_data)

            rights.append(rights_item)

        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        commerce_available_offer = cls(
            offer_version=offer_version,
            contract_target_id=contract_target_id,
            purchase_kind=purchase_kind,
            channels=channels,
            rights=rights,
            name=name,
            description=description,
        )

        return commerce_available_offer
