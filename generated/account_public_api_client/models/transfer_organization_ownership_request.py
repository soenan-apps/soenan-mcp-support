from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define

T = TypeVar("T", bound="TransferOrganizationOwnershipRequest")


@_attrs_define
class TransferOrganizationOwnershipRequest:
    """
    Attributes:
        target_subject (str):
        request_id (UUID):
        expected_revision (int):
    """

    target_subject: str
    request_id: UUID
    expected_revision: int

    def to_dict(self) -> dict[str, Any]:
        target_subject = self.target_subject

        request_id = str(self.request_id)

        expected_revision = self.expected_revision

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "targetSubject": target_subject,
                "requestId": request_id,
                "expectedRevision": expected_revision,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        target_subject = d.pop("targetSubject")

        request_id = UUID(d.pop("requestId"))

        expected_revision = d.pop("expectedRevision")

        transfer_organization_ownership_request = cls(
            target_subject=target_subject,
            request_id=request_id,
            expected_revision=expected_revision,
        )

        return transfer_organization_ownership_request
