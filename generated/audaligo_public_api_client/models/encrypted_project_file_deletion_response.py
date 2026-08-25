from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="EncryptedProjectFileDeletionResponse")


@_attrs_define
class EncryptedProjectFileDeletionResponse:
    """
    Attributes:
        ok (bool):
        deleted_file_id (str):
        idempotent (bool):
    """

    ok: bool
    deleted_file_id: str
    idempotent: bool

    def to_dict(self) -> dict[str, Any]:
        ok = self.ok

        deleted_file_id = self.deleted_file_id

        idempotent = self.idempotent

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "ok": ok,
                "deletedFileId": deleted_file_id,
                "idempotent": idempotent,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        ok = d.pop("ok")

        deleted_file_id = d.pop("deletedFileId")

        idempotent = d.pop("idempotent")

        encrypted_project_file_deletion_response = cls(
            ok=ok,
            deleted_file_id=deleted_file_id,
            idempotent=idempotent,
        )

        return encrypted_project_file_deletion_response
