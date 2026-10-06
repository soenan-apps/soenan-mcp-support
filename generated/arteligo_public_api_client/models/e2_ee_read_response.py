from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.e2_ee_read_response_commands import E2EeReadResponseCommands
    from ..models.e2_ee_read_scope_result import E2EeReadScopeResult


T = TypeVar("T", bound="E2EeReadResponse")


@_attrs_define
class E2EeReadResponse:
    """
    Attributes:
        scopes (list[E2EeReadScopeResult]):
        key_scopes (list[E2EeReadScopeResult]): Permitted organization scopes needed to unwrap requested project keys.
        commands (E2EeReadResponseCommands):
        server_time (int):
    """

    scopes: list[E2EeReadScopeResult]
    key_scopes: list[E2EeReadScopeResult]
    commands: E2EeReadResponseCommands
    server_time: int

    def to_dict(self) -> dict[str, Any]:
        scopes = []
        for scopes_item_data in self.scopes:
            scopes_item = scopes_item_data.to_dict()
            scopes.append(scopes_item)

        key_scopes = []
        for key_scopes_item_data in self.key_scopes:
            key_scopes_item = key_scopes_item_data.to_dict()
            key_scopes.append(key_scopes_item)

        commands = self.commands.to_dict()

        server_time = self.server_time

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "scopes": scopes,
                "key_scopes": key_scopes,
                "commands": commands,
                "server_time": server_time,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_read_response_commands import E2EeReadResponseCommands
        from ..models.e2_ee_read_scope_result import E2EeReadScopeResult

        d = dict(src_dict)
        scopes = []
        _scopes = d.pop("scopes")
        for scopes_item_data in _scopes:
            scopes_item = E2EeReadScopeResult.from_dict(scopes_item_data)

            scopes.append(scopes_item)

        key_scopes = []
        _key_scopes = d.pop("key_scopes")
        for key_scopes_item_data in _key_scopes:
            key_scopes_item = E2EeReadScopeResult.from_dict(key_scopes_item_data)

            key_scopes.append(key_scopes_item)

        commands = E2EeReadResponseCommands.from_dict(d.pop("commands"))

        server_time = d.pop("server_time")

        e2_ee_read_response = cls(
            scopes=scopes,
            key_scopes=key_scopes,
            commands=commands,
            server_time=server_time,
        )

        return e2_ee_read_response
