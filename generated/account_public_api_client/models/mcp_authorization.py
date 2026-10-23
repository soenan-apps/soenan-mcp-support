from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from dateutil.parser import isoparse
from typing_extensions import Self

from ..models.mcpo_auth_scope import MCPOAuthScope

T = TypeVar("T", bound="MCPAuthorization")


@_attrs_define
class MCPAuthorization:
    """
    Attributes:
        id (UUID):
        client_id (str):
        client_name (str):
        resource (str):
        scopes (list[MCPOAuthScope]):
        granted_at (datetime.datetime):
    """

    id: UUID
    client_id: str
    client_name: str
    resource: str
    scopes: list[MCPOAuthScope]
    granted_at: datetime.datetime

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        client_id = self.client_id

        client_name = self.client_name

        resource = self.resource

        scopes = []
        for scopes_item_data in self.scopes:
            scopes_item = scopes_item_data.value
            scopes.append(scopes_item)

        granted_at = self.granted_at.isoformat()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "clientId": client_id,
                "clientName": client_name,
                "resource": resource,
                "scopes": scopes,
                "grantedAt": granted_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        client_id = d.pop("clientId")

        client_name = d.pop("clientName")

        resource = d.pop("resource")

        scopes = []
        _scopes = d.pop("scopes")
        for scopes_item_data in _scopes:
            scopes_item = MCPOAuthScope(scopes_item_data)

            scopes.append(scopes_item)

        granted_at = isoparse(d.pop("grantedAt"))

        mcp_authorization = cls(
            id=id,
            client_id=client_id,
            client_name=client_name,
            resource=resource,
            scopes=scopes,
            granted_at=granted_at,
        )

        return mcp_authorization
