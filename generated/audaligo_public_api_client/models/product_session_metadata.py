from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.product_session_metadata_client_kind import (
    ProductSessionMetadataClientKind,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="ProductSessionMetadata")


@_attrs_define
class ProductSessionMetadata:
    """
    Attributes:
        id (str):
        issued_at (datetime.datetime):
        access_expires_at (datetime.datetime):
        refreshable (bool):
        realtime_available (bool): Whether this settled session may open the realtime transport.
        client_kind (ProductSessionMetadataClientKind):
        refresh_expires_at (datetime.datetime | None | Unset):
        refresh_recommended_after (datetime.datetime | None | Unset):
    """

    id: str
    issued_at: datetime.datetime
    access_expires_at: datetime.datetime
    refreshable: bool
    realtime_available: bool
    client_kind: ProductSessionMetadataClientKind
    refresh_expires_at: datetime.datetime | None | Unset = UNSET
    refresh_recommended_after: datetime.datetime | None | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        issued_at = self.issued_at.isoformat()

        access_expires_at = self.access_expires_at.isoformat()

        refreshable = self.refreshable

        realtime_available = self.realtime_available

        client_kind = self.client_kind.value

        refresh_expires_at: None | str | Unset
        if isinstance(self.refresh_expires_at, Unset):
            refresh_expires_at = UNSET
        elif isinstance(self.refresh_expires_at, datetime.datetime):
            refresh_expires_at = self.refresh_expires_at.isoformat()
        else:
            refresh_expires_at = self.refresh_expires_at

        refresh_recommended_after: None | str | Unset
        if isinstance(self.refresh_recommended_after, Unset):
            refresh_recommended_after = UNSET
        elif isinstance(self.refresh_recommended_after, datetime.datetime):
            refresh_recommended_after = self.refresh_recommended_after.isoformat()
        else:
            refresh_recommended_after = self.refresh_recommended_after

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "issuedAt": issued_at,
                "accessExpiresAt": access_expires_at,
                "refreshable": refreshable,
                "realtimeAvailable": realtime_available,
                "clientKind": client_kind,
            }
        )
        if refresh_expires_at is not UNSET:
            field_dict["refreshExpiresAt"] = refresh_expires_at
        if refresh_recommended_after is not UNSET:
            field_dict["refreshRecommendedAfter"] = refresh_recommended_after

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        id = d.pop("id")

        issued_at = datetime.datetime.fromisoformat(d.pop("issuedAt"))

        access_expires_at = datetime.datetime.fromisoformat(d.pop("accessExpiresAt"))

        refreshable = d.pop("refreshable")

        realtime_available = d.pop("realtimeAvailable")

        client_kind = ProductSessionMetadataClientKind(d.pop("clientKind"))

        def _parse_refresh_expires_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                refresh_expires_at_type_1 = datetime.datetime.fromisoformat(data)

                return refresh_expires_at_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        refresh_expires_at = _parse_refresh_expires_at(d.pop("refreshExpiresAt", UNSET))

        def _parse_refresh_recommended_after(
            data: object,
        ) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                refresh_recommended_after_type_1 = datetime.datetime.fromisoformat(data)

                return refresh_recommended_after_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        refresh_recommended_after = _parse_refresh_recommended_after(
            d.pop("refreshRecommendedAfter", UNSET)
        )

        product_session_metadata = cls(
            id=id,
            issued_at=issued_at,
            access_expires_at=access_expires_at,
            refreshable=refreshable,
            realtime_available=realtime_available,
            client_kind=client_kind,
            refresh_expires_at=refresh_expires_at,
            refresh_recommended_after=refresh_recommended_after,
        )

        return product_session_metadata
