from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="ReadProjectFile")


@_attrs_define
class ReadProjectFile:
    """
    Attributes:
        file_id (str):
        encrypted_object_id (str):
        original_filename (str):
        original_plaintext_size (int):
    """

    file_id: str
    encrypted_object_id: str
    original_filename: str
    original_plaintext_size: int

    def to_dict(self) -> dict[str, Any]:
        file_id = self.file_id

        encrypted_object_id = self.encrypted_object_id

        original_filename = self.original_filename

        original_plaintext_size = self.original_plaintext_size

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "fileId": file_id,
                "encryptedObjectId": encrypted_object_id,
                "originalFilename": original_filename,
                "originalPlaintextSize": original_plaintext_size,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        file_id = d.pop("fileId")

        encrypted_object_id = d.pop("encryptedObjectId")

        original_filename = d.pop("originalFilename")

        original_plaintext_size = d.pop("originalPlaintextSize")

        read_project_file = cls(
            file_id=file_id,
            encrypted_object_id=encrypted_object_id,
            original_filename=original_filename,
            original_plaintext_size=original_plaintext_size,
        )

        return read_project_file
