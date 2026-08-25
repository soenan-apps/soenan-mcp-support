from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.unauthenticated_product_session_kind import UnauthenticatedProductSessionKind
from ..types import UNSET, Unset

T = TypeVar("T", bound="UnauthenticatedProductSession")


@_attrs_define
class UnauthenticatedProductSession:
    """
    Attributes:
        kind (UnauthenticatedProductSessionKind):
        authenticated (bool):
        user (None | Unset):  Default: None.
    """

    kind: UnauthenticatedProductSessionKind
    authenticated: bool
    user: None | Unset = None

    def to_dict(self) -> dict[str, Any]:
        kind = self.kind.value

        authenticated = self.authenticated

        user = self.user

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "kind": kind,
                "authenticated": authenticated,
            }
        )
        if user is not UNSET:
            field_dict["user"] = user

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        kind = UnauthenticatedProductSessionKind(d.pop("kind"))

        authenticated = d.pop("authenticated")

        user = d.pop("user", UNSET)

        unauthenticated_product_session = cls(
            kind=kind,
            authenticated=authenticated,
            user=user,
        )

        return unauthenticated_product_session
