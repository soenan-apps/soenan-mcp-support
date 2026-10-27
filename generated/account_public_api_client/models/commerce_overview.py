from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.commerce_overview_owner_kind import CommerceOverviewOwnerKind
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.commerce_available_offer import CommerceAvailableOffer
    from ..models.commerce_purchase import CommercePurchase


T = TypeVar("T", bound="CommerceOverview")


@_attrs_define
class CommerceOverview:
    """
    Attributes:
        owner_kind (CommerceOverviewOwnerKind):
        purchases (list[CommercePurchase]):
        available_offers (list[CommerceAvailableOffer]):
        next_cursor (str | Unset):
    """

    owner_kind: CommerceOverviewOwnerKind
    purchases: list[CommercePurchase]
    available_offers: list[CommerceAvailableOffer]
    next_cursor: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        owner_kind = self.owner_kind.value

        purchases = []
        for purchases_item_data in self.purchases:
            purchases_item = purchases_item_data.to_dict()
            purchases.append(purchases_item)

        available_offers = []
        for available_offers_item_data in self.available_offers:
            available_offers_item = available_offers_item_data.to_dict()
            available_offers.append(available_offers_item)

        next_cursor = self.next_cursor

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "ownerKind": owner_kind,
                "purchases": purchases,
                "availableOffers": available_offers,
            }
        )
        if next_cursor is not UNSET:
            field_dict["nextCursor"] = next_cursor

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.commerce_available_offer import CommerceAvailableOffer
        from ..models.commerce_purchase import CommercePurchase

        d = dict(src_dict)
        owner_kind = CommerceOverviewOwnerKind(d.pop("ownerKind"))

        purchases = []
        _purchases = d.pop("purchases")
        for purchases_item_data in _purchases:
            purchases_item = CommercePurchase.from_dict(purchases_item_data)

            purchases.append(purchases_item)

        available_offers = []
        _available_offers = d.pop("availableOffers")
        for available_offers_item_data in _available_offers:
            available_offers_item = CommerceAvailableOffer.from_dict(
                available_offers_item_data
            )

            available_offers.append(available_offers_item)

        next_cursor = d.pop("nextCursor", UNSET)

        commerce_overview = cls(
            owner_kind=owner_kind,
            purchases=purchases,
            available_offers=available_offers,
            next_cursor=next_cursor,
        )

        return commerce_overview
