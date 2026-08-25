from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.encrypted_project_file_file_kind import EncryptedProjectFileFileKind
from ..types import UNSET, Unset, parse_datetime

T = TypeVar("T", bound="EncryptedProjectFile")


@_attrs_define
class EncryptedProjectFile:
    """
    Attributes:
        project_id (str):
        file_id (str):
        encrypted_object_id (str):
        created_by (str):
        file_kind (EncryptedProjectFileFileKind):
        original_filename (str):
        original_plaintext_size (int):
        mime_type (str):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
        mix_version_id (None | str | Unset):
    """

    project_id: str
    file_id: str
    encrypted_object_id: str
    created_by: str
    file_kind: EncryptedProjectFileFileKind
    original_filename: str
    original_plaintext_size: int
    mime_type: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    mix_version_id: None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        project_id = self.project_id

        file_id = self.file_id

        encrypted_object_id = self.encrypted_object_id

        created_by = self.created_by

        file_kind = self.file_kind.value

        original_filename = self.original_filename

        original_plaintext_size = self.original_plaintext_size

        mime_type = self.mime_type

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        mix_version_id: None | str | Unset
        if isinstance(self.mix_version_id, Unset):
            mix_version_id = UNSET
        else:
            mix_version_id = self.mix_version_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "projectId": project_id,
                "fileId": file_id,
                "encryptedObjectId": encrypted_object_id,
                "createdBy": created_by,
                "fileKind": file_kind,
                "originalFilename": original_filename,
                "originalPlaintextSize": original_plaintext_size,
                "mimeType": mime_type,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )
        if mix_version_id is not UNSET:
            field_dict["mixVersionId"] = mix_version_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        project_id = d.pop("projectId")

        file_id = d.pop("fileId")

        encrypted_object_id = d.pop("encryptedObjectId")

        created_by = d.pop("createdBy")

        file_kind = EncryptedProjectFileFileKind(d.pop("fileKind"))

        original_filename = d.pop("originalFilename")

        original_plaintext_size = d.pop("originalPlaintextSize")

        mime_type = d.pop("mimeType")

        created_at = parse_datetime(d.pop("createdAt"))

        updated_at = parse_datetime(d.pop("updatedAt"))

        def _parse_mix_version_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        mix_version_id = _parse_mix_version_id(d.pop("mixVersionId", UNSET))

        encrypted_project_file = cls(
            project_id=project_id,
            file_id=file_id,
            encrypted_object_id=encrypted_object_id,
            created_by=created_by,
            file_kind=file_kind,
            original_filename=original_filename,
            original_plaintext_size=original_plaintext_size,
            mime_type=mime_type,
            created_at=created_at,
            updated_at=updated_at,
            mix_version_id=mix_version_id,
        )

        return encrypted_project_file
