from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.invitation_membership import InvitationMembership
    from ..models.invitation_project import InvitationProject
    from ..models.invitation_state import InvitationState


T = TypeVar("T", bound="InvitationStatus")


@_attrs_define
class InvitationStatus:
    """
    Attributes:
        invitation (InvitationState):
        project (InvitationProject):
        next_action (str):
        membership (InvitationMembership | None | Unset):
    """

    invitation: InvitationState
    project: InvitationProject
    next_action: str
    membership: InvitationMembership | None | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        from ..models.invitation_membership import InvitationMembership

        invitation = self.invitation.to_dict()

        project = self.project.to_dict()

        next_action = self.next_action

        membership: dict[str, Any] | None | Unset
        if isinstance(self.membership, Unset):
            membership = UNSET
        elif isinstance(self.membership, InvitationMembership):
            membership = self.membership.to_dict()
        else:
            membership = self.membership

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "invitation": invitation,
                "project": project,
                "nextAction": next_action,
            }
        )
        if membership is not UNSET:
            field_dict["membership"] = membership

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.invitation_membership import InvitationMembership
        from ..models.invitation_project import InvitationProject
        from ..models.invitation_state import InvitationState

        d = dict(src_dict)
        invitation = InvitationState.from_dict(d.pop("invitation"))

        project = InvitationProject.from_dict(d.pop("project"))

        next_action = d.pop("nextAction")

        def _parse_membership(data: object) -> InvitationMembership | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                membership_type_1 = InvitationMembership.from_dict(data)

                return membership_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(InvitationMembership | None | Unset, data)

        membership = _parse_membership(d.pop("membership", UNSET))

        invitation_status = cls(
            invitation=invitation,
            project=project,
            next_action=next_action,
            membership=membership,
        )

        return invitation_status
