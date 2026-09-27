from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="StageFile")


@_attrs_define
class StageFile:
    """
    Attributes:
        file_id (str):
        relative_path (str):
    """

    file_id: str
    relative_path: str

    def to_dict(self) -> dict[str, Any]:
        file_id = self.file_id

        relative_path = self.relative_path

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "fileId": file_id,
                "relativePath": relative_path,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        file_id = d.pop("fileId")

        relative_path = d.pop("relativePath")

        stage_file = cls(
            file_id=file_id,
            relative_path=relative_path,
        )

        return stage_file
