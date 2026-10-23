from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.commerce_channel import CommerceChannel
from ..models.commerce_purchase_attempt_state import CommercePurchaseAttemptState
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.commerce_provider_start import CommerceProviderStart


T = TypeVar("T", bound="CommercePurchaseAttempt")


@_attrs_define
class CommercePurchaseAttempt:
    """
    Attributes:
        id (UUID):
        offer_version (str):
        channel (CommerceChannel):
        state (CommercePurchaseAttemptState):
        provider_result (CommerceProviderStart | Unset):
    """

    id: UUID
    offer_version: str
    channel: CommerceChannel
    state: CommercePurchaseAttemptState
    provider_result: CommerceProviderStart | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        offer_version = self.offer_version

        channel = self.channel.value

        state = self.state.value

        provider_result: dict[str, Any] | Unset = UNSET
        if not isinstance(self.provider_result, Unset):
            provider_result = self.provider_result.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "offerVersion": offer_version,
                "channel": channel,
                "state": state,
            }
        )
        if provider_result is not UNSET:
            field_dict["providerResult"] = provider_result

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.commerce_provider_start import CommerceProviderStart

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        offer_version = d.pop("offerVersion")

        channel = CommerceChannel(d.pop("channel"))

        state = CommercePurchaseAttemptState(d.pop("state"))

        _provider_result = d.pop("providerResult", UNSET)
        provider_result: CommerceProviderStart | Unset
        if isinstance(_provider_result, Unset):
            provider_result = UNSET
        else:
            provider_result = CommerceProviderStart.from_dict(_provider_result)

        commerce_purchase_attempt = cls(
            id=id,
            offer_version=offer_version,
            channel=channel,
            state=state,
            provider_result=provider_result,
        )

        return commerce_purchase_attempt
