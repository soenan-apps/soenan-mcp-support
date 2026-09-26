from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="InvitationHandoffClearBatch")


@_attrs_define
class InvitationHandoffClearBatch:
    """
    Attributes:
        has_more (bool):
    """

    has_more: bool

    def to_dict(self) -> dict[str, Any]:
        has_more = self.has_more

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "hasMore": has_more,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        has_more = d.pop("hasMore")

        invitation_handoff_clear_batch = cls(
            has_more=has_more,
        )

        return invitation_handoff_clear_batch
