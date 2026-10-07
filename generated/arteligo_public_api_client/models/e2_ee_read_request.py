from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.e2_ee_read_scope import E2EeReadScope


T = TypeVar("T", bound="E2EeReadRequest")


@_attrs_define
class E2EeReadRequest:
    """
    Attributes:
        scopes (list[E2EeReadScope]): Distinct scope IDs with at most 256 record IDs across all scopes.
        include_keys (bool | Unset):  Default: True.
    """

    scopes: list[E2EeReadScope]
    include_keys: bool | Unset = True

    def to_dict(self) -> dict[str, Any]:
        scopes = []
        for scopes_item_data in self.scopes:
            scopes_item = scopes_item_data.to_dict()
            scopes.append(scopes_item)

        include_keys = self.include_keys

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "scopes": scopes,
            }
        )
        if include_keys is not UNSET:
            field_dict["include_keys"] = include_keys

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_read_scope import E2EeReadScope

        d = dict(src_dict)
        scopes = []
        _scopes = d.pop("scopes")
        for scopes_item_data in _scopes:
            scopes_item = E2EeReadScope.from_dict(scopes_item_data)

            scopes.append(scopes_item)

        include_keys = d.pop("include_keys", UNSET)

        e2_ee_read_request = cls(
            scopes=scopes,
            include_keys=include_keys,
        )

        return e2_ee_read_request
