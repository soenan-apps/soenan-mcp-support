from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.e2_ee_envelope import E2EeEnvelope


T = TypeVar("T", bound="E2EeRotation")


@_attrs_define
class E2EeRotation:
    """
    Attributes:
        scope_id (str):
        expected_epoch (int):
        envelopes (list[E2EeEnvelope]):
        previous_key_ciphertext (str | Unset):
    """

    scope_id: str
    expected_epoch: int
    envelopes: list[E2EeEnvelope]
    previous_key_ciphertext: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        scope_id = self.scope_id

        expected_epoch = self.expected_epoch

        envelopes = []
        for envelopes_item_data in self.envelopes:
            envelopes_item = envelopes_item_data.to_dict()
            envelopes.append(envelopes_item)

        previous_key_ciphertext = self.previous_key_ciphertext

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "scope_id": scope_id,
                "expected_epoch": expected_epoch,
                "envelopes": envelopes,
            }
        )
        if previous_key_ciphertext is not UNSET:
            field_dict["previous_key_ciphertext"] = previous_key_ciphertext

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_envelope import E2EeEnvelope

        d = dict(src_dict)
        scope_id = d.pop("scope_id")

        expected_epoch = d.pop("expected_epoch")

        envelopes = []
        _envelopes = d.pop("envelopes")
        for envelopes_item_data in _envelopes:
            envelopes_item = E2EeEnvelope.from_dict(envelopes_item_data)

            envelopes.append(envelopes_item)

        previous_key_ciphertext = d.pop("previous_key_ciphertext", UNSET)

        e2_ee_rotation = cls(
            scope_id=scope_id,
            expected_epoch=expected_epoch,
            envelopes=envelopes,
            previous_key_ciphertext=previous_key_ciphertext,
        )

        return e2_ee_rotation
