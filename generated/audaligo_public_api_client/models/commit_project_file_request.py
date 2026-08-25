from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.commit_project_file_request_file_kind import CommitProjectFileRequestFileKind
from ..types import UNSET, Unset

T = TypeVar("T", bound="CommitProjectFileRequest")


@_attrs_define
class CommitProjectFileRequest:
    """
    Attributes:
        encrypted_object_id (str):
        file_kind (CommitProjectFileRequestFileKind):
        original_filename (str):
        original_plaintext_size (int):
        mix_version_id (str | Unset):
    """

    encrypted_object_id: str
    file_kind: CommitProjectFileRequestFileKind
    original_filename: str
    original_plaintext_size: int
    mix_version_id: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        encrypted_object_id = self.encrypted_object_id

        file_kind = self.file_kind.value

        original_filename = self.original_filename

        original_plaintext_size = self.original_plaintext_size

        mix_version_id = self.mix_version_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "encryptedObjectId": encrypted_object_id,
                "fileKind": file_kind,
                "originalFilename": original_filename,
                "originalPlaintextSize": original_plaintext_size,
            }
        )
        if mix_version_id is not UNSET:
            field_dict["mixVersionId"] = mix_version_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        encrypted_object_id = d.pop("encryptedObjectId")

        file_kind = CommitProjectFileRequestFileKind(d.pop("fileKind"))

        original_filename = d.pop("originalFilename")

        original_plaintext_size = d.pop("originalPlaintextSize")

        mix_version_id = d.pop("mixVersionId", UNSET)

        commit_project_file_request = cls(
            encrypted_object_id=encrypted_object_id,
            file_kind=file_kind,
            original_filename=original_filename,
            original_plaintext_size=original_plaintext_size,
            mix_version_id=mix_version_id,
        )

        return commit_project_file_request
