from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.e2_ee_owner_source_bundle import E2EeOwnerSourceBundle


T = TypeVar("T", bound="E2EeRootReplacementManifest")


@_attrs_define
class E2EeRootReplacementManifest:
    """
    Attributes:
        manifest_id (str):
        bundle (E2EeOwnerSourceBundle):
    """

    manifest_id: str
    bundle: E2EeOwnerSourceBundle

    def to_dict(self) -> dict[str, Any]:
        manifest_id = self.manifest_id

        bundle = self.bundle.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "manifest_id": manifest_id,
                "bundle": bundle,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.e2_ee_owner_source_bundle import E2EeOwnerSourceBundle

        d = dict(src_dict)
        manifest_id = d.pop("manifest_id")

        bundle = E2EeOwnerSourceBundle.from_dict(d.pop("bundle"))

        e2_ee_root_replacement_manifest = cls(
            manifest_id=manifest_id,
            bundle=bundle,
        )

        return e2_ee_root_replacement_manifest
