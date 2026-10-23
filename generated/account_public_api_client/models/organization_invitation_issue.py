from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from dateutil.parser import isoparse
from typing_extensions import Self

from ..models.email_submission import EmailSubmission

T = TypeVar("T", bound="OrganizationInvitationIssue")


@_attrs_define
class OrganizationInvitationIssue:
    """
    Attributes:
        invitation_id (UUID):
        submission (EmailSubmission): Acceptance by the configured adapter, or an unconfirmed submission. Neither
            confirms delivery.
        expires_at (datetime.datetime):
    """

    invitation_id: UUID
    submission: EmailSubmission
    expires_at: datetime.datetime

    def to_dict(self) -> dict[str, Any]:
        invitation_id = str(self.invitation_id)

        submission = self.submission.value

        expires_at = self.expires_at.isoformat()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "invitationId": invitation_id,
                "submission": submission,
                "expiresAt": expires_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        invitation_id = UUID(d.pop("invitationId"))

        submission = EmailSubmission(d.pop("submission"))

        expires_at = isoparse(d.pop("expiresAt"))

        organization_invitation_issue = cls(
            invitation_id=invitation_id,
            submission=submission,
            expires_at=expires_at,
        )

        return organization_invitation_issue
