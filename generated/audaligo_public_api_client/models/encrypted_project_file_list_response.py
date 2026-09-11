from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.encrypted_project_file import EncryptedProjectFile


T = TypeVar("T", bound="EncryptedProjectFileListResponse")


@_attrs_define
class EncryptedProjectFileListResponse:
    """
    Attributes:
        ok (bool):
        files (list[EncryptedProjectFile]):
    """

    ok: bool
    files: list[EncryptedProjectFile]

    def to_dict(self) -> dict[str, Any]:
        ok = self.ok

        files = []
        for files_item_data in self.files:
            files_item = files_item_data.to_dict()
            files.append(files_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "ok": ok,
                "files": files,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.encrypted_project_file import (
            EncryptedProjectFile,
        )

        d = dict(src_dict)
        ok = d.pop("ok")

        files = []
        _files = d.pop("files")
        for files_item_data in _files:
            files_item = EncryptedProjectFile.from_dict(files_item_data)

            files.append(files_item)

        encrypted_project_file_list_response = cls(
            ok=ok,
            files=files,
        )

        return encrypted_project_file_list_response
