from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.organization_invitation_detail import OrganizationInvitationDetail
    from ..models.organization_member_detail import OrganizationMemberDetail
    from ..models.organization_role_detail import OrganizationRoleDetail
    from ..models.organization_summary import OrganizationSummary


T = TypeVar("T", bound="OrganizationDetail")


@_attrs_define
class OrganizationDetail:
    """
    Attributes:
        organization (OrganizationSummary):
        current_account_subject (str):
        current_role_keys (list[str]):
        members (list[OrganizationMemberDetail] | Unset):
        roles (list[OrganizationRoleDetail] | Unset):
        invitations (list[OrganizationInvitationDetail] | Unset):
    """

    organization: OrganizationSummary
    current_account_subject: str
    current_role_keys: list[str]
    members: list[OrganizationMemberDetail] | Unset = UNSET
    roles: list[OrganizationRoleDetail] | Unset = UNSET
    invitations: list[OrganizationInvitationDetail] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        organization = self.organization.to_dict()

        current_account_subject = self.current_account_subject

        current_role_keys = self.current_role_keys

        members: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.members, Unset):
            members = []
            for members_item_data in self.members:
                members_item = members_item_data.to_dict()
                members.append(members_item)

        roles: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.roles, Unset):
            roles = []
            for roles_item_data in self.roles:
                roles_item = roles_item_data.to_dict()
                roles.append(roles_item)

        invitations: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.invitations, Unset):
            invitations = []
            for invitations_item_data in self.invitations:
                invitations_item = invitations_item_data.to_dict()
                invitations.append(invitations_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "organization": organization,
                "currentAccountSubject": current_account_subject,
                "currentRoleKeys": current_role_keys,
            }
        )
        if members is not UNSET:
            field_dict["members"] = members
        if roles is not UNSET:
            field_dict["roles"] = roles
        if invitations is not UNSET:
            field_dict["invitations"] = invitations

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.organization_invitation_detail import OrganizationInvitationDetail
        from ..models.organization_member_detail import OrganizationMemberDetail
        from ..models.organization_role_detail import OrganizationRoleDetail
        from ..models.organization_summary import OrganizationSummary

        d = dict(src_dict)
        organization = OrganizationSummary.from_dict(d.pop("organization"))

        current_account_subject = d.pop("currentAccountSubject")

        current_role_keys = cast(list[str], d.pop("currentRoleKeys"))

        _members = d.pop("members", UNSET)
        members: list[OrganizationMemberDetail] | Unset = UNSET
        if _members is not UNSET:
            members = []
            for members_item_data in _members:
                members_item = OrganizationMemberDetail.from_dict(members_item_data)

                members.append(members_item)

        _roles = d.pop("roles", UNSET)
        roles: list[OrganizationRoleDetail] | Unset = UNSET
        if _roles is not UNSET:
            roles = []
            for roles_item_data in _roles:
                roles_item = OrganizationRoleDetail.from_dict(roles_item_data)

                roles.append(roles_item)

        _invitations = d.pop("invitations", UNSET)
        invitations: list[OrganizationInvitationDetail] | Unset = UNSET
        if _invitations is not UNSET:
            invitations = []
            for invitations_item_data in _invitations:
                invitations_item = OrganizationInvitationDetail.from_dict(
                    invitations_item_data
                )

                invitations.append(invitations_item)

        organization_detail = cls(
            organization=organization,
            current_account_subject=current_account_subject,
            current_role_keys=current_role_keys,
            members=members,
            roles=roles,
            invitations=invitations,
        )

        return organization_detail
