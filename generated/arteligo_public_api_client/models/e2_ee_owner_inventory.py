from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.e2_ee_owner_authority import E2EeOwnerAuthority
    from ..models.e2_ee_owner_coverage_gap import E2EeOwnerCoverageGap
    from ..models.e2_ee_owner_inventory_organization import (
        E2EeOwnerInventoryOrganization,
    )
    from ..models.e2_ee_owner_inventory_project import E2EeOwnerInventoryProject


T = TypeVar("T", bound="E2EeOwnerInventory")


@_attrs_define
class E2EeOwnerInventory:
    """
    Attributes:
        organization (E2EeOwnerInventoryOrganization): Actual retained organization-key epochs; never infer a contiguous
            range. key_epoch is zero only when the organization scope has not been initialized.
        projects (list[E2EeOwnerInventoryProject]):
        missing_coverage (list[E2EeOwnerCoverageGap]):
        coverage_digest (str):
        owner_authority (E2EeOwnerAuthority):
    """

    organization: E2EeOwnerInventoryOrganization
    projects: list[E2EeOwnerInventoryProject]
    missing_coverage: list[E2EeOwnerCoverageGap]
    coverage_digest: str
    owner_authority: E2EeOwnerAuthority

    def to_dict(self) -> dict[str, Any]:
        organization = self.organization.to_dict()

        projects = []
        for projects_item_data in self.projects:
            projects_item = projects_item_data.to_dict()
            projects.append(projects_item)

        missing_coverage = []
        for missing_coverage_item_data in self.missing_coverage:
            missing_coverage_item = missing_coverage_item_data.to_dict()
            missing_coverage.append(missing_coverage_item)

        coverage_digest = self.coverage_digest

        owner_authority = self.owner_authority.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "organization": organization,
                "projects": projects,
                "missing_coverage": missing_coverage,
                "coverage_digest": coverage_digest,
                "owner_authority": owner_authority,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_owner_authority import E2EeOwnerAuthority
        from ..models.e2_ee_owner_coverage_gap import E2EeOwnerCoverageGap
        from ..models.e2_ee_owner_inventory_organization import (
            E2EeOwnerInventoryOrganization,
        )
        from ..models.e2_ee_owner_inventory_project import E2EeOwnerInventoryProject

        d = dict(src_dict)
        organization = E2EeOwnerInventoryOrganization.from_dict(d.pop("organization"))

        projects = []
        _projects = d.pop("projects")
        for projects_item_data in _projects:
            projects_item = E2EeOwnerInventoryProject.from_dict(projects_item_data)

            projects.append(projects_item)

        missing_coverage = []
        _missing_coverage = d.pop("missing_coverage")
        for missing_coverage_item_data in _missing_coverage:
            missing_coverage_item = E2EeOwnerCoverageGap.from_dict(
                missing_coverage_item_data
            )

            missing_coverage.append(missing_coverage_item)

        coverage_digest = d.pop("coverage_digest")

        owner_authority = E2EeOwnerAuthority.from_dict(d.pop("owner_authority"))

        e2_ee_owner_inventory = cls(
            organization=organization,
            projects=projects,
            missing_coverage=missing_coverage,
            coverage_digest=coverage_digest,
            owner_authority=owner_authority,
        )

        return e2_ee_owner_inventory
