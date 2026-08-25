from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.encrypted_project_file import EncryptedProjectFile


T = TypeVar("T", bound="EncryptedProjectFileResponse")


@_attrs_define
class EncryptedProjectFileResponse:
    """
    Attributes:
        ok (bool):
        file (EncryptedProjectFile):
        idempotent (bool | Unset):
    """

    ok: bool
    file: EncryptedProjectFile
    idempotent: bool | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        ok = self.ok

        file = self.file.to_dict()

        idempotent = self.idempotent

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "ok": ok,
                "file": file,
            }
        )
        if idempotent is not UNSET:
            field_dict["idempotent"] = idempotent

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.encrypted_project_file import EncryptedProjectFile

        d = dict(src_dict)
        ok = d.pop("ok")

        file = EncryptedProjectFile.from_dict(d.pop("file"))

        idempotent = d.pop("idempotent", UNSET)

        encrypted_project_file_response = cls(
            ok=ok,
            file=file,
            idempotent=idempotent,
        )

        return encrypted_project_file_response
