from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.file_check_level import FileCheckLevel
from ..types import UNSET, Unset

T = TypeVar("T", bound="FileCheck")


@_attrs_define
class FileCheck:
    """
    Attributes:
        id (str):
        label (str):
        level (FileCheckLevel):
        detail (None | str | Unset):
    """

    id: str
    label: str
    level: FileCheckLevel
    detail: None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        label = self.label

        level = self.level.value

        detail: None | str | Unset
        if isinstance(self.detail, Unset):
            detail = UNSET
        else:
            detail = self.detail

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "label": label,
                "level": level,
            }
        )
        if detail is not UNSET:
            field_dict["detail"] = detail

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        label = d.pop("label")

        level = FileCheckLevel(d.pop("level"))

        def _parse_detail(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        detail = _parse_detail(d.pop("detail", UNSET))

        file_check = cls(
            id=id,
            label=label,
            level=level,
            detail=detail,
        )

        return file_check
