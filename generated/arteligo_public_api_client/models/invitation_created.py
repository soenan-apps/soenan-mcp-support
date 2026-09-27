from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.invitation_summary import InvitationSummary


T = TypeVar("T", bound="InvitationCreated")


@_attrs_define
class InvitationCreated:
    """
    Attributes:
        invitation (InvitationSummary):
        fragment_url (None | str | Unset):
    """

    invitation: InvitationSummary
    fragment_url: None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        invitation = self.invitation.to_dict()

        fragment_url: None | str | Unset
        if isinstance(self.fragment_url, Unset):
            fragment_url = UNSET
        else:
            fragment_url = self.fragment_url

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "invitation": invitation,
            }
        )
        if fragment_url is not UNSET:
            field_dict["fragmentUrl"] = fragment_url

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.invitation_summary import InvitationSummary

        d = dict(src_dict)
        invitation = InvitationSummary.from_dict(d.pop("invitation"))

        def _parse_fragment_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        fragment_url = _parse_fragment_url(d.pop("fragmentUrl", UNSET))

        invitation_created = cls(
            invitation=invitation,
            fragment_url=fragment_url,
        )

        return invitation_created
