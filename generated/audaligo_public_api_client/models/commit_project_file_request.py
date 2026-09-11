from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.commit_project_file_request_file_kind import (
    CommitProjectFileRequestFileKind,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.project_file_entry_intent import ProjectFileEntryIntent


T = TypeVar("T", bound="CommitProjectFileRequest")


@_attrs_define
class CommitProjectFileRequest:
    """
    Attributes:
        encrypted_object_id (str):
        file_kind (CommitProjectFileRequestFileKind):
        original_filename (str):
        original_plaintext_size (int):
        entry_intent (ProjectFileEntryIntent):
        mime_type (str | Unset):
    """

    encrypted_object_id: str
    file_kind: CommitProjectFileRequestFileKind
    original_filename: str
    original_plaintext_size: int
    entry_intent: ProjectFileEntryIntent
    mime_type: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        encrypted_object_id = self.encrypted_object_id

        file_kind = self.file_kind.value

        original_filename = self.original_filename

        original_plaintext_size = self.original_plaintext_size

        entry_intent = self.entry_intent.to_dict()

        mime_type = self.mime_type

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "encryptedObjectId": encrypted_object_id,
                "fileKind": file_kind,
                "originalFilename": original_filename,
                "originalPlaintextSize": original_plaintext_size,
                "entryIntent": entry_intent,
            }
        )
        if mime_type is not UNSET:
            field_dict["mimeType"] = mime_type

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.project_file_entry_intent import (
            ProjectFileEntryIntent,
        )

        d = dict(src_dict)
        encrypted_object_id = d.pop("encryptedObjectId")

        file_kind = CommitProjectFileRequestFileKind(d.pop("fileKind"))

        original_filename = d.pop("originalFilename")

        original_plaintext_size = d.pop("originalPlaintextSize")

        entry_intent = ProjectFileEntryIntent.from_dict(d.pop("entryIntent"))

        mime_type = d.pop("mimeType", UNSET)

        commit_project_file_request = cls(
            encrypted_object_id=encrypted_object_id,
            file_kind=file_kind,
            original_filename=original_filename,
            original_plaintext_size=original_plaintext_size,
            entry_intent=entry_intent,
            mime_type=mime_type,
        )

        return commit_project_file_request
