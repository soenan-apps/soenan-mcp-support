from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.encrypted_object_manifest import EncryptedObjectManifest


T = TypeVar("T", bound="PutManifestRequest")


@_attrs_define
class PutManifestRequest:
    """
    Attributes:
        manifest (EncryptedObjectManifest):
    """

    manifest: EncryptedObjectManifest

    def to_dict(self) -> dict[str, Any]:
        manifest = self.manifest.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "manifest": manifest,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.encrypted_object_manifest import (
            EncryptedObjectManifest,
        )

        d = dict(src_dict)
        manifest = EncryptedObjectManifest.from_dict(d.pop("manifest"))

        put_manifest_request = cls(
            manifest=manifest,
        )

        return put_manifest_request
