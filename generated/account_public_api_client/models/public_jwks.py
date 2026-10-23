from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.public_jwk import PublicJWK


T = TypeVar("T", bound="PublicJWKS")


@_attrs_define
class PublicJWKS:
    """
    Attributes:
        keys (list[PublicJWK]):
    """

    keys: list[PublicJWK]

    def to_dict(self) -> dict[str, Any]:
        keys = []
        for keys_item_data in self.keys:
            keys_item = keys_item_data.to_dict()
            keys.append(keys_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "keys": keys,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.public_jwk import PublicJWK

        d = dict(src_dict)
        keys = []
        _keys = d.pop("keys")
        for keys_item_data in _keys:
            keys_item = PublicJWK.from_dict(keys_item_data)

            keys.append(keys_item)

        public_jwks = cls(
            keys=keys,
        )

        return public_jwks
