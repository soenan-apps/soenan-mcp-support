from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.owner_custody_organization_admission_kind import (
    OwnerCustodyOrganizationAdmissionKind,
)

if TYPE_CHECKING:
    from ..models.owner_custody_organization_admission_recovery_root import (
        OwnerCustodyOrganizationAdmissionRecoveryRoot,
    )


T = TypeVar("T", bound="OwnerCustodyOrganizationAdmission")


@_attrs_define
class OwnerCustodyOrganizationAdmission:
    """
    Attributes:
        kind (OwnerCustodyOrganizationAdmissionKind):
        organization_id (str):
        recovery_root (OwnerCustodyOrganizationAdmissionRecoveryRoot):
    """

    kind: OwnerCustodyOrganizationAdmissionKind
    organization_id: str
    recovery_root: OwnerCustodyOrganizationAdmissionRecoveryRoot

    def to_dict(self) -> dict[str, Any]:
        kind = self.kind.value

        organization_id = self.organization_id

        recovery_root = self.recovery_root.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "kind": kind,
                "organization_id": organization_id,
                "recovery_root": recovery_root,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.owner_custody_organization_admission_recovery_root import (
            OwnerCustodyOrganizationAdmissionRecoveryRoot,
        )

        d = dict(src_dict)
        kind = OwnerCustodyOrganizationAdmissionKind(d.pop("kind"))

        organization_id = d.pop("organization_id")

        recovery_root = OwnerCustodyOrganizationAdmissionRecoveryRoot.from_dict(
            d.pop("recovery_root")
        )

        owner_custody_organization_admission = cls(
            kind=kind,
            organization_id=organization_id,
            recovery_root=recovery_root,
        )

        return owner_custody_organization_admission
