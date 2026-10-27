from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.e2_ee_key_operation_reference_kind import E2EeKeyOperationReferenceKind
from ..types import UNSET, Unset

T = TypeVar("T", bound="E2EeKeyOperationReference")


@_attrs_define
class E2EeKeyOperationReference:
    """
    Attributes:
        kind (E2EeKeyOperationReferenceKind):
        account_subject (str):
        origin_reference (str):
        organization_id (str | Unset):
        scope_id (str | Unset):
        device_id (str | Unset):
        certificate_digest (str | Unset):
        root_evidence_digest (str | Unset):
        transfer_operation_id (str | Unset):
    """

    kind: E2EeKeyOperationReferenceKind
    account_subject: str
    origin_reference: str
    organization_id: str | Unset = UNSET
    scope_id: str | Unset = UNSET
    device_id: str | Unset = UNSET
    certificate_digest: str | Unset = UNSET
    root_evidence_digest: str | Unset = UNSET
    transfer_operation_id: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        kind = self.kind.value

        account_subject = self.account_subject

        origin_reference = self.origin_reference

        organization_id = self.organization_id

        scope_id = self.scope_id

        device_id = self.device_id

        certificate_digest = self.certificate_digest

        root_evidence_digest = self.root_evidence_digest

        transfer_operation_id = self.transfer_operation_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "kind": kind,
                "account_subject": account_subject,
                "origin_reference": origin_reference,
            }
        )
        if organization_id is not UNSET:
            field_dict["organization_id"] = organization_id
        if scope_id is not UNSET:
            field_dict["scope_id"] = scope_id
        if device_id is not UNSET:
            field_dict["device_id"] = device_id
        if certificate_digest is not UNSET:
            field_dict["certificate_digest"] = certificate_digest
        if root_evidence_digest is not UNSET:
            field_dict["root_evidence_digest"] = root_evidence_digest
        if transfer_operation_id is not UNSET:
            field_dict["transfer_operation_id"] = transfer_operation_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        kind = E2EeKeyOperationReferenceKind(d.pop("kind"))

        account_subject = d.pop("account_subject")

        origin_reference = d.pop("origin_reference")

        organization_id = d.pop("organization_id", UNSET)

        scope_id = d.pop("scope_id", UNSET)

        device_id = d.pop("device_id", UNSET)

        certificate_digest = d.pop("certificate_digest", UNSET)

        root_evidence_digest = d.pop("root_evidence_digest", UNSET)

        transfer_operation_id = d.pop("transfer_operation_id", UNSET)

        e2_ee_key_operation_reference = cls(
            kind=kind,
            account_subject=account_subject,
            origin_reference=origin_reference,
            organization_id=organization_id,
            scope_id=scope_id,
            device_id=device_id,
            certificate_digest=certificate_digest,
            root_evidence_digest=root_evidence_digest,
            transfer_operation_id=transfer_operation_id,
        )

        return e2_ee_key_operation_reference
