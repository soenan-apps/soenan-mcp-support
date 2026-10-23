from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from dateutil.parser import isoparse
from typing_extensions import Self

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.account_profile import AccountProfile


T = TypeVar("T", bound="SessionView")


@_attrs_define
class SessionView:
    """
    Attributes:
        authenticated (bool):
        profile (AccountProfile | None | Unset):
        access_expires_at (datetime.datetime | Unset):
        refresh_recommended_after (datetime.datetime | Unset):
        refreshable (bool | Unset):
    """

    authenticated: bool
    profile: AccountProfile | None | Unset = UNSET
    access_expires_at: datetime.datetime | Unset = UNSET
    refresh_recommended_after: datetime.datetime | Unset = UNSET
    refreshable: bool | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        from ..models.account_profile import AccountProfile

        authenticated = self.authenticated

        profile: dict[str, Any] | None | Unset
        if isinstance(self.profile, Unset):
            profile = UNSET
        elif isinstance(self.profile, AccountProfile):
            profile = self.profile.to_dict()
        else:
            profile = self.profile

        access_expires_at: str | Unset = UNSET
        if not isinstance(self.access_expires_at, Unset):
            access_expires_at = self.access_expires_at.isoformat()

        refresh_recommended_after: str | Unset = UNSET
        if not isinstance(self.refresh_recommended_after, Unset):
            refresh_recommended_after = self.refresh_recommended_after.isoformat()

        refreshable = self.refreshable

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "authenticated": authenticated,
            }
        )
        if profile is not UNSET:
            field_dict["profile"] = profile
        if access_expires_at is not UNSET:
            field_dict["accessExpiresAt"] = access_expires_at
        if refresh_recommended_after is not UNSET:
            field_dict["refreshRecommendedAfter"] = refresh_recommended_after
        if refreshable is not UNSET:
            field_dict["refreshable"] = refreshable

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.account_profile import AccountProfile

        d = dict(src_dict)
        authenticated = d.pop("authenticated")

        def _parse_profile(data: object) -> AccountProfile | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                profile_type_1 = AccountProfile.from_dict(data)

                return profile_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(AccountProfile | None | Unset, data)

        profile = _parse_profile(d.pop("profile", UNSET))

        _access_expires_at = d.pop("accessExpiresAt", UNSET)
        access_expires_at: datetime.datetime | Unset
        if isinstance(_access_expires_at, Unset):
            access_expires_at = UNSET
        else:
            access_expires_at = isoparse(_access_expires_at)

        _refresh_recommended_after = d.pop("refreshRecommendedAfter", UNSET)
        refresh_recommended_after: datetime.datetime | Unset
        if isinstance(_refresh_recommended_after, Unset):
            refresh_recommended_after = UNSET
        else:
            refresh_recommended_after = isoparse(_refresh_recommended_after)

        refreshable = d.pop("refreshable", UNSET)

        session_view = cls(
            authenticated=authenticated,
            profile=profile,
            access_expires_at=access_expires_at,
            refresh_recommended_after=refresh_recommended_after,
            refreshable=refreshable,
        )

        return session_view
