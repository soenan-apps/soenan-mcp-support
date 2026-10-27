from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.mail_link_accepted_status import MailLinkAcceptedStatus

T = TypeVar("T", bound="MailLinkAccepted")


@_attrs_define
class MailLinkAccepted:
    """
    Attributes:
        status (MailLinkAcceptedStatus):
    """

    status: MailLinkAcceptedStatus

    def to_dict(self) -> dict[str, Any]:
        status = self.status.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "status": status,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        status = MailLinkAcceptedStatus(d.pop("status"))

        mail_link_accepted = cls(
            status=status,
        )

        return mail_link_accepted
