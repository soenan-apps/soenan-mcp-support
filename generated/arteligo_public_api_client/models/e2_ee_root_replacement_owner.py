from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.e2_ee_owner_artifact import E2EeOwnerArtifact
    from ..models.e2_ee_owner_authority import E2EeOwnerAuthority
    from ..models.e2_ee_owner_binding_proof import E2EeOwnerBindingProof
    from ..models.e2_ee_owner_candidate_result import E2EeOwnerCandidateResult
    from ..models.e2_ee_owner_inventory import E2EeOwnerInventory
    from ..models.e2_ee_owner_project_source_artifact import (
        E2EeOwnerProjectSourceArtifact,
    )
    from ..models.e2_ee_owner_source_index_artifact import E2EeOwnerSourceIndexArtifact
    from ..models.e2_ee_root_replacement_manifest import E2EeRootReplacementManifest


T = TypeVar("T", bound="E2EeRootReplacementOwner")


@_attrs_define
class E2EeRootReplacementOwner:
    """
    Attributes:
        organization_id (str):
        bindings (list[E2EeOwnerBindingProof]):
        candidates (list[E2EeOwnerCandidateResult]):
        preparations (list[E2EeOwnerArtifact]):
        manifests (list[E2EeOwnerSourceIndexArtifact]):
        sources (list[E2EeOwnerProjectSourceArtifact]):
        manifest_bundles (list[E2EeRootReplacementManifest]):
        authority (E2EeOwnerAuthority | Unset):
        inventory (E2EeOwnerInventory | Unset):
        keyring (E2EeOwnerArtifact | Unset):
    """

    organization_id: str
    bindings: list[E2EeOwnerBindingProof]
    candidates: list[E2EeOwnerCandidateResult]
    preparations: list[E2EeOwnerArtifact]
    manifests: list[E2EeOwnerSourceIndexArtifact]
    sources: list[E2EeOwnerProjectSourceArtifact]
    manifest_bundles: list[E2EeRootReplacementManifest]
    authority: E2EeOwnerAuthority | Unset = UNSET
    inventory: E2EeOwnerInventory | Unset = UNSET
    keyring: E2EeOwnerArtifact | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        organization_id = self.organization_id

        bindings = []
        for bindings_item_data in self.bindings:
            bindings_item = bindings_item_data.to_dict()
            bindings.append(bindings_item)

        candidates = []
        for candidates_item_data in self.candidates:
            candidates_item = candidates_item_data.to_dict()
            candidates.append(candidates_item)

        preparations = []
        for preparations_item_data in self.preparations:
            preparations_item = preparations_item_data.to_dict()
            preparations.append(preparations_item)

        manifests = []
        for manifests_item_data in self.manifests:
            manifests_item = manifests_item_data.to_dict()
            manifests.append(manifests_item)

        sources = []
        for sources_item_data in self.sources:
            sources_item = sources_item_data.to_dict()
            sources.append(sources_item)

        manifest_bundles = []
        for manifest_bundles_item_data in self.manifest_bundles:
            manifest_bundles_item = manifest_bundles_item_data.to_dict()
            manifest_bundles.append(manifest_bundles_item)

        authority: dict[str, Any] | Unset = UNSET
        if not isinstance(self.authority, Unset):
            authority = self.authority.to_dict()

        inventory: dict[str, Any] | Unset = UNSET
        if not isinstance(self.inventory, Unset):
            inventory = self.inventory.to_dict()

        keyring: dict[str, Any] | Unset = UNSET
        if not isinstance(self.keyring, Unset):
            keyring = self.keyring.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "organization_id": organization_id,
                "bindings": bindings,
                "candidates": candidates,
                "preparations": preparations,
                "manifests": manifests,
                "sources": sources,
                "manifest_bundles": manifest_bundles,
            }
        )
        if authority is not UNSET:
            field_dict["authority"] = authority
        if inventory is not UNSET:
            field_dict["inventory"] = inventory
        if keyring is not UNSET:
            field_dict["keyring"] = keyring

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.e2_ee_owner_artifact import E2EeOwnerArtifact
        from ..models.e2_ee_owner_authority import E2EeOwnerAuthority
        from ..models.e2_ee_owner_binding_proof import E2EeOwnerBindingProof
        from ..models.e2_ee_owner_candidate_result import E2EeOwnerCandidateResult
        from ..models.e2_ee_owner_inventory import E2EeOwnerInventory
        from ..models.e2_ee_owner_project_source_artifact import (
            E2EeOwnerProjectSourceArtifact,
        )
        from ..models.e2_ee_owner_source_index_artifact import (
            E2EeOwnerSourceIndexArtifact,
        )
        from ..models.e2_ee_root_replacement_manifest import E2EeRootReplacementManifest

        d = dict(src_dict)
        organization_id = d.pop("organization_id")

        bindings = []
        _bindings = d.pop("bindings")
        for bindings_item_data in _bindings:
            bindings_item = E2EeOwnerBindingProof.from_dict(bindings_item_data)

            bindings.append(bindings_item)

        candidates = []
        _candidates = d.pop("candidates")
        for candidates_item_data in _candidates:
            candidates_item = E2EeOwnerCandidateResult.from_dict(candidates_item_data)

            candidates.append(candidates_item)

        preparations = []
        _preparations = d.pop("preparations")
        for preparations_item_data in _preparations:
            preparations_item = E2EeOwnerArtifact.from_dict(preparations_item_data)

            preparations.append(preparations_item)

        manifests = []
        _manifests = d.pop("manifests")
        for manifests_item_data in _manifests:
            manifests_item = E2EeOwnerSourceIndexArtifact.from_dict(manifests_item_data)

            manifests.append(manifests_item)

        sources = []
        _sources = d.pop("sources")
        for sources_item_data in _sources:
            sources_item = E2EeOwnerProjectSourceArtifact.from_dict(sources_item_data)

            sources.append(sources_item)

        manifest_bundles = []
        _manifest_bundles = d.pop("manifest_bundles")
        for manifest_bundles_item_data in _manifest_bundles:
            manifest_bundles_item = E2EeRootReplacementManifest.from_dict(
                manifest_bundles_item_data
            )

            manifest_bundles.append(manifest_bundles_item)

        _authority = d.pop("authority", UNSET)
        authority: E2EeOwnerAuthority | Unset
        if isinstance(_authority, Unset):
            authority = UNSET
        else:
            authority = E2EeOwnerAuthority.from_dict(_authority)

        _inventory = d.pop("inventory", UNSET)
        inventory: E2EeOwnerInventory | Unset
        if isinstance(_inventory, Unset):
            inventory = UNSET
        else:
            inventory = E2EeOwnerInventory.from_dict(_inventory)

        _keyring = d.pop("keyring", UNSET)
        keyring: E2EeOwnerArtifact | Unset
        if isinstance(_keyring, Unset):
            keyring = UNSET
        else:
            keyring = E2EeOwnerArtifact.from_dict(_keyring)

        e2_ee_root_replacement_owner = cls(
            organization_id=organization_id,
            bindings=bindings,
            candidates=candidates,
            preparations=preparations,
            manifests=manifests,
            sources=sources,
            manifest_bundles=manifest_bundles,
            authority=authority,
            inventory=inventory,
            keyring=keyring,
        )

        return e2_ee_root_replacement_owner
