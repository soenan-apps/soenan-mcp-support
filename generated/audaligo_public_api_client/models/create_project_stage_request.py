from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.stage_content import StageContent


T = TypeVar("T", bound="CreateProjectStageRequest")


@_attrs_define
class CreateProjectStageRequest:
    """
    Attributes:
        contents (list[StageContent]):
        label (None | str | Unset): Optional display name; empty or whitespace-only values clear it.
    """

    contents: list[StageContent]
    label: None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        contents = []
        for contents_item_data in self.contents:
            contents_item = contents_item_data.to_dict()
            contents.append(contents_item)

        label: None | str | Unset
        if isinstance(self.label, Unset):
            label = UNSET
        else:
            label = self.label

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "contents": contents,
            }
        )
        if label is not UNSET:
            field_dict["label"] = label

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.stage_content import StageContent

        d = dict(src_dict)
        contents = []
        _contents = d.pop("contents")
        for contents_item_data in _contents:
            contents_item = StageContent.from_dict(contents_item_data)

            contents.append(contents_item)

        def _parse_label(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        label = _parse_label(d.pop("label", UNSET))

        create_project_stage_request = cls(
            contents=contents,
            label=label,
        )

        return create_project_stage_request
