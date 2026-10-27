from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.e2_ee_owner_source_manifest_format import E2EeOwnerSourceManifestFormat

if TYPE_CHECKING:
    from ..models.e2_ee_owner_authority import E2EeOwnerAuthority
    from ..models.e2_ee_owner_issuer_admission import E2EeOwnerIssuerAdmission
    from ..models.e2_ee_owner_source_index_entry import E2EeOwnerSourceIndexEntry


T = TypeVar("T", bound="E2EeOwnerSourceManifest")


@_attrs_define
class E2EeOwnerSourceManifest:
    """
    Attributes:
        format_ (E2EeOwnerSourceManifestFormat):
        organization_id (str):
        manifest_id (str):
        owner_authority (E2EeOwnerAuthority):
        issuer_admission (E2EeOwnerIssuerAdmission): The original source-root and exact immutable certificate references
            selected when this command was signed. Later certificates cannot qualify or replace this evidence.
        entries (list[E2EeOwnerSourceIndexEntry]): Complete cumulative index, unique and ordered by decoded 32-byte
            project_key. Selected predecessor entries never change.
    """

    format_: E2EeOwnerSourceManifestFormat
    organization_id: str
    manifest_id: str
    owner_authority: E2EeOwnerAuthority
    issuer_admission: E2EeOwnerIssuerAdmission
    entries: list[E2EeOwnerSourceIndexEntry]

    def to_dict(self) -> dict[str, Any]:
        format_ = self.format_.value

        organization_id = self.organization_id

        manifest_id = self.manifest_id

        owner_authority = self.owner_authority.to_dict()

        issuer_admission = self.issuer_admission.to_dict()

        entries = []
        for entries_item_data in self.entries:
            entries_item = entries_item_data.to_dict()
            entries.append(entries_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "format": format_,
                "organization_id": organization_id,
                "manifest_id": manifest_id,
                "owner_authority": owner_authority,
                "issuer_admission": issuer_admission,
                "entries": entries,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.e2_ee_owner_authority import E2EeOwnerAuthority
        from ..models.e2_ee_owner_issuer_admission import E2EeOwnerIssuerAdmission
        from ..models.e2_ee_owner_source_index_entry import E2EeOwnerSourceIndexEntry

        d = dict(src_dict)
        format_ = E2EeOwnerSourceManifestFormat(d.pop("format"))

        organization_id = d.pop("organization_id")

        manifest_id = d.pop("manifest_id")

        owner_authority = E2EeOwnerAuthority.from_dict(d.pop("owner_authority"))

        issuer_admission = E2EeOwnerIssuerAdmission.from_dict(d.pop("issuer_admission"))

        entries = []
        _entries = d.pop("entries")
        for entries_item_data in _entries:
            entries_item = E2EeOwnerSourceIndexEntry.from_dict(entries_item_data)

            entries.append(entries_item)

        e2_ee_owner_source_manifest = cls(
            format_=format_,
            organization_id=organization_id,
            manifest_id=manifest_id,
            owner_authority=owner_authority,
            issuer_admission=issuer_admission,
            entries=entries,
        )

        return e2_ee_owner_source_manifest
