from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.e2_ee_object_manifest import E2EeObjectManifest


T = TypeVar("T", bound="E2EeObjectDescriptor")


@_attrs_define
class E2EeObjectDescriptor:
    """
    Attributes:
        manifest (E2EeObjectManifest):
        state (str):
        expires_at (int):
    """

    manifest: E2EeObjectManifest
    state: str
    expires_at: int

    def to_dict(self) -> dict[str, Any]:
        manifest = self.manifest.to_dict()

        state = self.state

        expires_at = self.expires_at

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "manifest": manifest,
                "state": state,
                "expires_at": expires_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_object_manifest import E2EeObjectManifest

        d = dict(src_dict)
        manifest = E2EeObjectManifest.from_dict(d.pop("manifest"))

        state = d.pop("state")

        expires_at = d.pop("expires_at")

        e2_ee_object_descriptor = cls(
            manifest=manifest,
            state=state,
            expires_at=expires_at,
        )

        return e2_ee_object_descriptor
