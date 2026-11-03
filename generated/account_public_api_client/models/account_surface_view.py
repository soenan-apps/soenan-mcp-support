from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.account_surface_view_surface import AccountSurfaceViewSurface

if TYPE_CHECKING:
    from ..models.account_profile import AccountProfile


T = TypeVar("T", bound="AccountSurfaceView")


@_attrs_define
class AccountSurfaceView:
    """
    Attributes:
        surface (AccountSurfaceViewSurface):
        profile (AccountProfile):
    """

    surface: AccountSurfaceViewSurface
    profile: AccountProfile

    def to_dict(self) -> dict[str, Any]:
        surface = self.surface.value

        profile = self.profile.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "surface": surface,
                "profile": profile,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.account_profile import AccountProfile

        d = dict(src_dict)
        surface = AccountSurfaceViewSurface(d.pop("surface"))

        profile = AccountProfile.from_dict(d.pop("profile"))

        account_surface_view = cls(
            surface=surface,
            profile=profile,
        )

        return account_surface_view
