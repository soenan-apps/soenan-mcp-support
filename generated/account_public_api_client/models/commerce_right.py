from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.commerce_right_kind import CommerceRightKind
from ..types import UNSET, Unset

T = TypeVar("T", bound="CommerceRight")


@_attrs_define
class CommerceRight:
    """
    Attributes:
        kind (CommerceRightKind):
        product_id (str):
        features (list[str] | Unset):
        edition (str | Unset):
        release_ids (list[str] | Unset):
        seats (int | Unset):
        storage_blocks (int | Unset):
    """

    kind: CommerceRightKind
    product_id: str
    features: list[str] | Unset = UNSET
    edition: str | Unset = UNSET
    release_ids: list[str] | Unset = UNSET
    seats: int | Unset = UNSET
    storage_blocks: int | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        kind = self.kind.value

        product_id = self.product_id

        features: list[str] | Unset = UNSET
        if not isinstance(self.features, Unset):
            features = self.features

        edition = self.edition

        release_ids: list[str] | Unset = UNSET
        if not isinstance(self.release_ids, Unset):
            release_ids = self.release_ids

        seats = self.seats

        storage_blocks = self.storage_blocks

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "kind": kind,
                "productId": product_id,
            }
        )
        if features is not UNSET:
            field_dict["features"] = features
        if edition is not UNSET:
            field_dict["edition"] = edition
        if release_ids is not UNSET:
            field_dict["releaseIds"] = release_ids
        if seats is not UNSET:
            field_dict["seats"] = seats
        if storage_blocks is not UNSET:
            field_dict["storageBlocks"] = storage_blocks

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        kind = CommerceRightKind(d.pop("kind"))

        product_id = d.pop("productId")

        features = cast(list[str], d.pop("features", UNSET))

        edition = d.pop("edition", UNSET)

        release_ids = cast(list[str], d.pop("releaseIds", UNSET))

        seats = d.pop("seats", UNSET)

        storage_blocks = d.pop("storageBlocks", UNSET)

        commerce_right = cls(
            kind=kind,
            product_id=product_id,
            features=features,
            edition=edition,
            release_ids=release_ids,
            seats=seats,
            storage_blocks=storage_blocks,
        )

        return commerce_right
