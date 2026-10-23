from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.commerce_channel import CommerceChannel
from ..types import UNSET, Unset

T = TypeVar("T", bound="CommerceBeginRequest")


@_attrs_define
class CommerceBeginRequest:
    """
    Attributes:
        offer_version (str):
        channel (CommerceChannel):
        idempotency_key (str):
        quantity (int | Unset):  Default: 1.
    """

    offer_version: str
    channel: CommerceChannel
    idempotency_key: str
    quantity: int | Unset = 1

    def to_dict(self) -> dict[str, Any]:
        offer_version = self.offer_version

        channel = self.channel.value

        idempotency_key = self.idempotency_key

        quantity = self.quantity

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "offerVersion": offer_version,
                "channel": channel,
                "idempotencyKey": idempotency_key,
            }
        )
        if quantity is not UNSET:
            field_dict["quantity"] = quantity

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        offer_version = d.pop("offerVersion")

        channel = CommerceChannel(d.pop("channel"))

        idempotency_key = d.pop("idempotencyKey")

        quantity = d.pop("quantity", UNSET)

        commerce_begin_request = cls(
            offer_version=offer_version,
            channel=channel,
            idempotency_key=idempotency_key,
            quantity=quantity,
        )

        return commerce_begin_request
