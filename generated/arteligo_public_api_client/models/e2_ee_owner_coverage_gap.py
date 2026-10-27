from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="E2EeOwnerCoverageGap")


@_attrs_define
class E2EeOwnerCoverageGap:
    """
    Attributes:
        project_id (str):
        key_epoch (int):
    """

    project_id: str
    key_epoch: int

    def to_dict(self) -> dict[str, Any]:
        project_id = self.project_id

        key_epoch = self.key_epoch

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "project_id": project_id,
                "key_epoch": key_epoch,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        project_id = d.pop("project_id")

        key_epoch = d.pop("key_epoch")

        e2_ee_owner_coverage_gap = cls(
            project_id=project_id,
            key_epoch=key_epoch,
        )

        return e2_ee_owner_coverage_gap
