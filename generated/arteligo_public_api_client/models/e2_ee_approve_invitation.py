from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.e2_ee_envelope import E2EeEnvelope


T = TypeVar("T", bound="E2EeApproveInvitation")


@_attrs_define
class E2EeApproveInvitation:
    """
    Attributes:
        request_id (str):
        key_epoch (int):
        envelopes (list[E2EeEnvelope]):
    """

    request_id: str
    key_epoch: int
    envelopes: list[E2EeEnvelope]

    def to_dict(self) -> dict[str, Any]:
        request_id = self.request_id

        key_epoch = self.key_epoch

        envelopes = []
        for envelopes_item_data in self.envelopes:
            envelopes_item = envelopes_item_data.to_dict()
            envelopes.append(envelopes_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "request_id": request_id,
                "key_epoch": key_epoch,
                "envelopes": envelopes,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_envelope import E2EeEnvelope

        d = dict(src_dict)
        request_id = d.pop("request_id")

        key_epoch = d.pop("key_epoch")

        envelopes = []
        _envelopes = d.pop("envelopes")
        for envelopes_item_data in _envelopes:
            envelopes_item = E2EeEnvelope.from_dict(envelopes_item_data)

            envelopes.append(envelopes_item)

        e2_ee_approve_invitation = cls(
            request_id=request_id,
            key_epoch=key_epoch,
            envelopes=envelopes,
        )

        return e2_ee_approve_invitation
