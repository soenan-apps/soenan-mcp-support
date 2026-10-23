from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.mcp_authorization import MCPAuthorization


T = TypeVar("T", bound="MCPAuthorizationList")


@_attrs_define
class MCPAuthorizationList:
    """
    Attributes:
        authorizations (list[MCPAuthorization]):
    """

    authorizations: list[MCPAuthorization]

    def to_dict(self) -> dict[str, Any]:
        authorizations = []
        for authorizations_item_data in self.authorizations:
            authorizations_item = authorizations_item_data.to_dict()
            authorizations.append(authorizations_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "authorizations": authorizations,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.mcp_authorization import MCPAuthorization

        d = dict(src_dict)
        authorizations = []
        _authorizations = d.pop("authorizations")
        for authorizations_item_data in _authorizations:
            authorizations_item = MCPAuthorization.from_dict(authorizations_item_data)

            authorizations.append(authorizations_item)

        mcp_authorization_list = cls(
            authorizations=authorizations,
        )

        return mcp_authorization_list
