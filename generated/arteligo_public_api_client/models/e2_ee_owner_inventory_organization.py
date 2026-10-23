from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="E2EeOwnerInventoryOrganization")


@_attrs_define
class E2EeOwnerInventoryOrganization:
    """Actual retained organization-key epochs; never infer a contiguous range. key_epoch is zero only when the
    organization scope has not been initialized.

        Attributes:
            organization_id (str):
            key_epoch (int):
            epochs (list[int]):
    """

    organization_id: str
    key_epoch: int
    epochs: list[int]

    def to_dict(self) -> dict[str, Any]:
        organization_id = self.organization_id

        key_epoch = self.key_epoch

        epochs = self.epochs

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "organization_id": organization_id,
                "key_epoch": key_epoch,
                "epochs": epochs,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        organization_id = d.pop("organization_id")

        key_epoch = d.pop("key_epoch")

        epochs = cast(list[int], d.pop("epochs"))

        e2_ee_owner_inventory_organization = cls(
            organization_id=organization_id,
            key_epoch=key_epoch,
            epochs=epochs,
        )

        return e2_ee_owner_inventory_organization
