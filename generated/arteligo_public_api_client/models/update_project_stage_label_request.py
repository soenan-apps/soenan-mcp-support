from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="UpdateProjectStageLabelRequest")


@_attrs_define
class UpdateProjectStageLabelRequest:
    """
    Attributes:
        expected_revision (int):
        label (None | str): Single-line display name; null, empty or whitespace-only clears it.
    """

    expected_revision: int
    label: None | str

    def to_dict(self) -> dict[str, Any]:
        expected_revision = self.expected_revision

        label: None | str
        label = self.label

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "expectedRevision": expected_revision,
                "label": label,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        expected_revision = d.pop("expectedRevision")

        def _parse_label(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        label = _parse_label(d.pop("label"))

        update_project_stage_label_request = cls(
            expected_revision=expected_revision,
            label=label,
        )

        return update_project_stage_label_request
