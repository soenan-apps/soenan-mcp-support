from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.commerce_provider_start_kind import CommerceProviderStartKind
from ..types import UNSET, Unset

T = TypeVar("T", bound="CommerceProviderStart")


@_attrs_define
class CommerceProviderStart:
    """
    Attributes:
        kind (CommerceProviderStartKind):
        id (str | Unset):
        url (str | Unset):
        product_id (str | Unset):
        owner_binding (str | Unset):
        base_plan_id (str | Unset):
        offer_id (str | Unset):
    """

    kind: CommerceProviderStartKind
    id: str | Unset = UNSET
    url: str | Unset = UNSET
    product_id: str | Unset = UNSET
    owner_binding: str | Unset = UNSET
    base_plan_id: str | Unset = UNSET
    offer_id: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        kind = self.kind.value

        id = self.id

        url = self.url

        product_id = self.product_id

        owner_binding = self.owner_binding

        base_plan_id = self.base_plan_id

        offer_id = self.offer_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "kind": kind,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id
        if url is not UNSET:
            field_dict["url"] = url
        if product_id is not UNSET:
            field_dict["productId"] = product_id
        if owner_binding is not UNSET:
            field_dict["ownerBinding"] = owner_binding
        if base_plan_id is not UNSET:
            field_dict["basePlanId"] = base_plan_id
        if offer_id is not UNSET:
            field_dict["offerId"] = offer_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        kind = CommerceProviderStartKind(d.pop("kind"))

        id = d.pop("id", UNSET)

        url = d.pop("url", UNSET)

        product_id = d.pop("productId", UNSET)

        owner_binding = d.pop("ownerBinding", UNSET)

        base_plan_id = d.pop("basePlanId", UNSET)

        offer_id = d.pop("offerId", UNSET)

        commerce_provider_start = cls(
            kind=kind,
            id=id,
            url=url,
            product_id=product_id,
            owner_binding=owner_binding,
            base_plan_id=base_plan_id,
            offer_id=offer_id,
        )

        return commerce_provider_start
