from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.accepted_invitation_state import AcceptedInvitationState
    from ..models.invitation_membership import InvitationMembership
    from ..models.invitation_project import InvitationProject


T = TypeVar("T", bound="InvitationAccepted")


@_attrs_define
class InvitationAccepted:
    """
    Attributes:
        invitation (AcceptedInvitationState):
        project (InvitationProject):
        membership (InvitationMembership):
        next_action (str):
    """

    invitation: AcceptedInvitationState
    project: InvitationProject
    membership: InvitationMembership
    next_action: str

    def to_dict(self) -> dict[str, Any]:
        invitation = self.invitation.to_dict()

        project = self.project.to_dict()

        membership = self.membership.to_dict()

        next_action = self.next_action

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "invitation": invitation,
                "project": project,
                "membership": membership,
                "nextAction": next_action,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.accepted_invitation_state import AcceptedInvitationState
        from ..models.invitation_membership import InvitationMembership
        from ..models.invitation_project import InvitationProject

        d = dict(src_dict)
        invitation = AcceptedInvitationState.from_dict(d.pop("invitation"))

        project = InvitationProject.from_dict(d.pop("project"))

        membership = InvitationMembership.from_dict(d.pop("membership"))

        next_action = d.pop("nextAction")

        invitation_accepted = cls(
            invitation=invitation,
            project=project,
            membership=membership,
            next_action=next_action,
        )

        return invitation_accepted
