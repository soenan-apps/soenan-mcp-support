from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="ResolveCommentRequest")


@_attrs_define
class ResolveCommentRequest:
    """
    Attributes:
        resolved (bool):
    """

    resolved: bool

    def to_dict(self) -> dict[str, Any]:
        resolved = self.resolved

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "resolved": resolved,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        resolved = d.pop("resolved")

        resolve_comment_request = cls(
            resolved=resolved,
        )

        return resolve_comment_request
