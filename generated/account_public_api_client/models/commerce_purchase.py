from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ..models.commerce_channel import CommerceChannel
from ..models.commerce_purchase_kind import CommercePurchaseKind
from ..models.commerce_right_state import CommerceRightState
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.commerce_right import CommerceRight


T = TypeVar("T", bound="CommercePurchase")


@_attrs_define
class CommercePurchase:
    """
    Attributes:
        id (UUID):
        offer_version (str):
        name (str):
        purchase_kind (CommercePurchaseKind):
        channel (CommerceChannel):
        state (CommerceRightState):
        revision (int):
        rights (list[CommerceRight]):
        cancel_at_period_end (bool):
        manual_contract_conflict (bool):
        purchased_at (datetime.datetime | Unset):
        period_end (datetime.datetime | Unset):
        terms_version_id (UUID | Unset):
    """

    id: UUID
    offer_version: str
    name: str
    purchase_kind: CommercePurchaseKind
    channel: CommerceChannel
    state: CommerceRightState
    revision: int
    rights: list[CommerceRight]
    cancel_at_period_end: bool
    manual_contract_conflict: bool
    purchased_at: datetime.datetime | Unset = UNSET
    period_end: datetime.datetime | Unset = UNSET
    terms_version_id: UUID | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        offer_version = self.offer_version

        name = self.name

        purchase_kind = self.purchase_kind.value

        channel = self.channel.value

        state = self.state.value

        revision = self.revision

        rights = []
        for rights_item_data in self.rights:
            rights_item = rights_item_data.to_dict()
            rights.append(rights_item)

        cancel_at_period_end = self.cancel_at_period_end

        manual_contract_conflict = self.manual_contract_conflict

        purchased_at: str | Unset = UNSET
        if not isinstance(self.purchased_at, Unset):
            purchased_at = self.purchased_at.isoformat()

        period_end: str | Unset = UNSET
        if not isinstance(self.period_end, Unset):
            period_end = self.period_end.isoformat()

        terms_version_id: str | Unset = UNSET
        if not isinstance(self.terms_version_id, Unset):
            terms_version_id = str(self.terms_version_id)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "offerVersion": offer_version,
                "name": name,
                "purchaseKind": purchase_kind,
                "channel": channel,
                "state": state,
                "revision": revision,
                "rights": rights,
                "cancelAtPeriodEnd": cancel_at_period_end,
                "manualContractConflict": manual_contract_conflict,
            }
        )
        if purchased_at is not UNSET:
            field_dict["purchasedAt"] = purchased_at
        if period_end is not UNSET:
            field_dict["periodEnd"] = period_end
        if terms_version_id is not UNSET:
            field_dict["termsVersionId"] = terms_version_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.commerce_right import CommerceRight

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        offer_version = d.pop("offerVersion")

        name = d.pop("name")

        purchase_kind = CommercePurchaseKind(d.pop("purchaseKind"))

        channel = CommerceChannel(d.pop("channel"))

        state = CommerceRightState(d.pop("state"))

        revision = d.pop("revision")

        rights = []
        _rights = d.pop("rights")
        for rights_item_data in _rights:
            rights_item = CommerceRight.from_dict(rights_item_data)

            rights.append(rights_item)

        cancel_at_period_end = d.pop("cancelAtPeriodEnd")

        manual_contract_conflict = d.pop("manualContractConflict")

        _purchased_at = d.pop("purchasedAt", UNSET)
        purchased_at: datetime.datetime | Unset
        if isinstance(_purchased_at, Unset):
            purchased_at = UNSET
        else:
            purchased_at = isoparse(_purchased_at)

        _period_end = d.pop("periodEnd", UNSET)
        period_end: datetime.datetime | Unset
        if isinstance(_period_end, Unset):
            period_end = UNSET
        else:
            period_end = isoparse(_period_end)

        _terms_version_id = d.pop("termsVersionId", UNSET)
        terms_version_id: UUID | Unset
        if isinstance(_terms_version_id, Unset):
            terms_version_id = UNSET
        else:
            terms_version_id = UUID(_terms_version_id)

        commerce_purchase = cls(
            id=id,
            offer_version=offer_version,
            name=name,
            purchase_kind=purchase_kind,
            channel=channel,
            state=state,
            revision=revision,
            rights=rights,
            cancel_at_period_end=cancel_at_period_end,
            manual_contract_conflict=manual_contract_conflict,
            purchased_at=purchased_at,
            period_end=period_end,
            terms_version_id=terms_version_id,
        )

        return commerce_purchase
