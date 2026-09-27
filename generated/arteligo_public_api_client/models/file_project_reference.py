from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.file_project_reference_kind import FileProjectReferenceKind

T = TypeVar("T", bound="FileProjectReference")


@_attrs_define
class FileProjectReference:
    """
    Attributes:
        kind (FileProjectReferenceKind):
        file_id (str):
    """

    kind: FileProjectReferenceKind
    file_id: str

    def to_dict(self) -> dict[str, Any]:
        kind = self.kind.value

        file_id = self.file_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "kind": kind,
                "fileId": file_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        kind = FileProjectReferenceKind(d.pop("kind"))

        file_id = d.pop("fileId")

        file_project_reference = cls(
            kind=kind,
            file_id=file_id,
        )

        return file_project_reference
