from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="LogoutProductSessionResponse")


@_attrs_define
class LogoutProductSessionResponse:
    """
    Attributes:
        ok (bool):
        remote_revoked (bool):
    """

    ok: bool
    remote_revoked: bool

    def to_dict(self) -> dict[str, Any]:
        ok = self.ok

        remote_revoked = self.remote_revoked

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "ok": ok,
                "remoteRevoked": remote_revoked,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        ok = d.pop("ok")

        remote_revoked = d.pop("remoteRevoked")

        logout_product_session_response = cls(
            ok=ok,
            remote_revoked=remote_revoked,
        )

        return logout_product_session_response
