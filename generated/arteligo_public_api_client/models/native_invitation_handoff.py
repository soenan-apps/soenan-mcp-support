from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from dateutil.parser import isoparse
from typing_extensions import Self

T = TypeVar("T", bound="NativeInvitationHandoff")


@_attrs_define
class NativeInvitationHandoff:
    """
    Attributes:
        binding (str):
        expires_at (datetime.datetime):
    """

    binding: str
    expires_at: datetime.datetime

    def to_dict(self) -> dict[str, Any]:
        binding = self.binding

        expires_at = self.expires_at.isoformat()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "binding": binding,
                "expiresAt": expires_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        binding = d.pop("binding")

        expires_at = isoparse(d.pop("expiresAt"))

        native_invitation_handoff = cls(
            binding=binding,
            expires_at=expires_at,
        )

        return native_invitation_handoff
