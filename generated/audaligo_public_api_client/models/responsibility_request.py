from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="ResponsibilityRequest")


@_attrs_define
class ResponsibilityRequest:
    """
    Attributes:
        expected_revision (int):
        waiting_on_membership_id (None | str | Unset):
    """

    expected_revision: int
    waiting_on_membership_id: None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        expected_revision = self.expected_revision

        waiting_on_membership_id: None | str | Unset
        if isinstance(self.waiting_on_membership_id, Unset):
            waiting_on_membership_id = UNSET
        else:
            waiting_on_membership_id = self.waiting_on_membership_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "expectedRevision": expected_revision,
            }
        )
        if waiting_on_membership_id is not UNSET:
            field_dict["waitingOnMembershipId"] = waiting_on_membership_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        expected_revision = d.pop("expectedRevision")

        def _parse_waiting_on_membership_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        waiting_on_membership_id = _parse_waiting_on_membership_id(d.pop("waitingOnMembershipId", UNSET))

        responsibility_request = cls(
            expected_revision=expected_revision,
            waiting_on_membership_id=waiting_on_membership_id,
        )

        return responsibility_request
