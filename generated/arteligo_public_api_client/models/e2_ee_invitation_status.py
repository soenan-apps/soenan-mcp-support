from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.e2_ee_signed_command import E2EeSignedCommand


T = TypeVar("T", bound="E2EeInvitationStatus")


@_attrs_define
class E2EeInvitationStatus:
    """
    Attributes:
        request_id (str):
        invitation_id (str):
        project_id (str):
        account_subject (str):
        state (str):
        request (E2EeSignedCommand):
    """

    request_id: str
    invitation_id: str
    project_id: str
    account_subject: str
    state: str
    request: E2EeSignedCommand

    def to_dict(self) -> dict[str, Any]:
        request_id = self.request_id

        invitation_id = self.invitation_id

        project_id = self.project_id

        account_subject = self.account_subject

        state = self.state

        request = self.request.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "request_id": request_id,
                "invitation_id": invitation_id,
                "project_id": project_id,
                "account_subject": account_subject,
                "state": state,
                "request": request,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_signed_command import E2EeSignedCommand

        d = dict(src_dict)
        request_id = d.pop("request_id")

        invitation_id = d.pop("invitation_id")

        project_id = d.pop("project_id")

        account_subject = d.pop("account_subject")

        state = d.pop("state")

        request = E2EeSignedCommand.from_dict(d.pop("request"))

        e2_ee_invitation_status = cls(
            request_id=request_id,
            invitation_id=invitation_id,
            project_id=project_id,
            account_subject=account_subject,
            state=state,
            request=request,
        )

        return e2_ee_invitation_status
