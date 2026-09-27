from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.stage_content_purpose import StageContentPurpose

if TYPE_CHECKING:
    from ..models.stage_file import StageFile


T = TypeVar("T", bound="StageContent")


@_attrs_define
class StageContent:
    """
    Attributes:
        id (str):
        purpose (StageContentPurpose):
        title (str):
        files (list[StageFile]):
    """

    id: str
    purpose: StageContentPurpose
    title: str
    files: list[StageFile]

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        purpose = self.purpose.value

        title = self.title

        files = []
        for files_item_data in self.files:
            files_item = files_item_data.to_dict()
            files.append(files_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "purpose": purpose,
                "title": title,
                "files": files,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.stage_file import StageFile

        d = dict(src_dict)
        id = d.pop("id")

        purpose = StageContentPurpose(d.pop("purpose"))

        title = d.pop("title")

        files = []
        _files = d.pop("files")
        for files_item_data in _files:
            files_item = StageFile.from_dict(files_item_data)

            files.append(files_item)

        stage_content = cls(
            id=id,
            purpose=purpose,
            title=title,
            files=files,
        )

        return stage_content
