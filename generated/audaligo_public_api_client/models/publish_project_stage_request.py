from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="PublishProjectStageRequest")


@_attrs_define
class PublishProjectStageRequest:
    """
    Attributes:
        expected_revision (int):
    """

    expected_revision: int

    def to_dict(self) -> dict[str, Any]:
        expected_revision = self.expected_revision

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "expectedRevision": expected_revision,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        expected_revision = d.pop("expectedRevision")

        publish_project_stage_request = cls(
            expected_revision=expected_revision,
        )

        return publish_project_stage_request
