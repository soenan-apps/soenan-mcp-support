from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.mix_version import MixVersion


T = TypeVar("T", bound="VersionEnvelope")


@_attrs_define
class VersionEnvelope:
    """
    Attributes:
        version (MixVersion):
    """

    version: MixVersion

    def to_dict(self) -> dict[str, Any]:
        version = self.version.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "version": version,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.mix_version import MixVersion

        d = dict(src_dict)
        version = MixVersion.from_dict(d.pop("version"))

        version_envelope = cls(
            version=version,
        )

        return version_envelope
