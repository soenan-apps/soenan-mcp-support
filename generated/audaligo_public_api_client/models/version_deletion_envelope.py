from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="VersionDeletionEnvelope")


@_attrs_define
class VersionDeletionEnvelope:
    """
    Attributes:
        deleted_version_id (str):
    """

    deleted_version_id: str

    def to_dict(self) -> dict[str, Any]:
        deleted_version_id = self.deleted_version_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "deletedVersionId": deleted_version_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        deleted_version_id = d.pop("deletedVersionId")

        version_deletion_envelope = cls(
            deleted_version_id=deleted_version_id,
        )

        return version_deletion_envelope
