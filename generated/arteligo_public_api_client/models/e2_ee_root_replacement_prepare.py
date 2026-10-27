from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.e2_ee_key_operation_dependency_manifest import (
        E2EeKeyOperationDependencyManifest,
    )
    from ..models.e2_ee_owner_issuer_root import E2EeOwnerIssuerRoot


T = TypeVar("T", bound="E2EeRootReplacementPrepare")


@_attrs_define
class E2EeRootReplacementPrepare:
    """
    Attributes:
        operation_id (str):
        issuer_device_id (str):
        expected_root (E2EeOwnerIssuerRoot):
        dependency_manifest (E2EeKeyOperationDependencyManifest):
    """

    operation_id: str
    issuer_device_id: str
    expected_root: E2EeOwnerIssuerRoot
    dependency_manifest: E2EeKeyOperationDependencyManifest

    def to_dict(self) -> dict[str, Any]:
        operation_id = self.operation_id

        issuer_device_id = self.issuer_device_id

        expected_root = self.expected_root.to_dict()

        dependency_manifest = self.dependency_manifest.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "operation_id": operation_id,
                "issuer_device_id": issuer_device_id,
                "expected_root": expected_root,
                "dependency_manifest": dependency_manifest,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.e2_ee_key_operation_dependency_manifest import (
            E2EeKeyOperationDependencyManifest,
        )
        from ..models.e2_ee_owner_issuer_root import E2EeOwnerIssuerRoot

        d = dict(src_dict)
        operation_id = d.pop("operation_id")

        issuer_device_id = d.pop("issuer_device_id")

        expected_root = E2EeOwnerIssuerRoot.from_dict(d.pop("expected_root"))

        dependency_manifest = E2EeKeyOperationDependencyManifest.from_dict(
            d.pop("dependency_manifest")
        )

        e2_ee_root_replacement_prepare = cls(
            operation_id=operation_id,
            issuer_device_id=issuer_device_id,
            expected_root=expected_root,
            dependency_manifest=dependency_manifest,
        )

        return e2_ee_root_replacement_prepare
