from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.member_actor_kind import MemberActorKind

if TYPE_CHECKING:
    from ..models.member_identity import MemberIdentity


T = TypeVar("T", bound="MemberActor")


@_attrs_define
class MemberActor:
    """
    Attributes:
        kind (MemberActorKind):
        member (MemberIdentity):
    """

    kind: MemberActorKind
    member: MemberIdentity

    def to_dict(self) -> dict[str, Any]:
        kind = self.kind.value

        member = self.member.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "kind": kind,
                "member": member,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.member_identity import MemberIdentity

        d = dict(src_dict)
        kind = MemberActorKind(d.pop("kind"))

        member = MemberIdentity.from_dict(d.pop("member"))

        member_actor = cls(
            kind=kind,
            member=member,
        )

        return member_actor
