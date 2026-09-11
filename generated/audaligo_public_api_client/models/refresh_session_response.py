from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.product_session_metadata import ProductSessionMetadata


T = TypeVar("T", bound="RefreshSessionResponse")


@_attrs_define
class RefreshSessionResponse:
    """
    Attributes:
        ok (bool):
        session (ProductSessionMetadata):
    """

    ok: bool
    session: ProductSessionMetadata

    def to_dict(self) -> dict[str, Any]:
        ok = self.ok

        session = self.session.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "ok": ok,
                "session": session,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.product_session_metadata import (
            ProductSessionMetadata,
        )

        d = dict(src_dict)
        ok = d.pop("ok")

        session = ProductSessionMetadata.from_dict(d.pop("session"))

        refresh_session_response = cls(
            ok=ok,
            session=session,
        )

        return refresh_session_response
