from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.member_identity import MemberIdentity


T = TypeVar("T", bound="Responsibility")


@_attrs_define
class Responsibility:
    """
    Attributes:
        revision (int):
        waiting_on (MemberIdentity | None | Unset):
    """

    revision: int
    waiting_on: MemberIdentity | None | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        from ..models.member_identity import MemberIdentity

        revision = self.revision

        waiting_on: dict[str, Any] | None | Unset
        if isinstance(self.waiting_on, Unset):
            waiting_on = UNSET
        elif isinstance(self.waiting_on, MemberIdentity):
            waiting_on = self.waiting_on.to_dict()
        else:
            waiting_on = self.waiting_on

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "revision": revision,
            }
        )
        if waiting_on is not UNSET:
            field_dict["waitingOn"] = waiting_on

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.member_identity import MemberIdentity

        d = dict(src_dict)
        revision = d.pop("revision")

        def _parse_waiting_on(data: object) -> MemberIdentity | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                waiting_on_type_1 = MemberIdentity.from_dict(data)

                return waiting_on_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(MemberIdentity | None | Unset, data)

        waiting_on = _parse_waiting_on(d.pop("waitingOn", UNSET))

        responsibility = cls(
            revision=revision,
            waiting_on=waiting_on,
        )

        return responsibility
