from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from dateutil.parser import isoparse
from typing_extensions import Self

from ..types import UNSET, Unset

T = TypeVar("T", bound="PasskeyView")


@_attrs_define
class PasskeyView:
    """
    Attributes:
        passkey_id (UUID):
        name (str):
        created_at (datetime.datetime):
        backup_eligible (bool):
        backed_up (bool):
        last_used_at (datetime.datetime | Unset):
    """

    passkey_id: UUID
    name: str
    created_at: datetime.datetime
    backup_eligible: bool
    backed_up: bool
    last_used_at: datetime.datetime | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        passkey_id = str(self.passkey_id)

        name = self.name

        created_at = self.created_at.isoformat()

        backup_eligible = self.backup_eligible

        backed_up = self.backed_up

        last_used_at: str | Unset = UNSET
        if not isinstance(self.last_used_at, Unset):
            last_used_at = self.last_used_at.isoformat()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "passkeyId": passkey_id,
                "name": name,
                "createdAt": created_at,
                "backupEligible": backup_eligible,
                "backedUp": backed_up,
            }
        )
        if last_used_at is not UNSET:
            field_dict["lastUsedAt"] = last_used_at

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        passkey_id = UUID(d.pop("passkeyId"))

        name = d.pop("name")

        created_at = isoparse(d.pop("createdAt"))

        backup_eligible = d.pop("backupEligible")

        backed_up = d.pop("backedUp")

        _last_used_at = d.pop("lastUsedAt", UNSET)
        last_used_at: datetime.datetime | Unset
        if isinstance(_last_used_at, Unset):
            last_used_at = UNSET
        else:
            last_used_at = isoparse(_last_used_at)

        passkey_view = cls(
            passkey_id=passkey_id,
            name=name,
            created_at=created_at,
            backup_eligible=backup_eligible,
            backed_up=backed_up,
            last_used_at=last_used_at,
        )

        return passkey_view
