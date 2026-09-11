from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.stage_content import StageContent


T = TypeVar("T", bound="UpdateProjectStageRequest")


@_attrs_define
class UpdateProjectStageRequest:
    """
    Attributes:
        expected_revision (int):
        contents (list[StageContent]):
    """

    expected_revision: int
    contents: list[StageContent]

    def to_dict(self) -> dict[str, Any]:
        expected_revision = self.expected_revision

        contents = []
        for contents_item_data in self.contents:
            contents_item = contents_item_data.to_dict()
            contents.append(contents_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "expectedRevision": expected_revision,
                "contents": contents,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.stage_content import StageContent

        d = dict(src_dict)
        expected_revision = d.pop("expectedRevision")

        contents = []
        _contents = d.pop("contents")
        for contents_item_data in _contents:
            contents_item = StageContent.from_dict(contents_item_data)

            contents.append(contents_item)

        update_project_stage_request = cls(
            expected_revision=expected_revision,
            contents=contents,
        )

        return update_project_stage_request
