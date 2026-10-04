from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.e2_ee_record_kind import E2EeRecordKind

if TYPE_CHECKING:
    from ..models.e2_ee_signed_command import E2EeSignedCommand


T = TypeVar("T", bound="E2EeRecord")


@_attrs_define
class E2EeRecord:
    """
    Attributes:
        record_id (str):
        kind (E2EeRecordKind):
        revision (int):
        cursor (int):
        key_epoch (int):
        ciphertext (str):
        deleted (bool):
        author_device_id (str):
        signed_command (E2EeSignedCommand):
    """

    record_id: str
    kind: E2EeRecordKind
    revision: int
    cursor: int
    key_epoch: int
    ciphertext: str
    deleted: bool
    author_device_id: str
    signed_command: E2EeSignedCommand

    def to_dict(self) -> dict[str, Any]:
        record_id = self.record_id

        kind = self.kind.value

        revision = self.revision

        cursor = self.cursor

        key_epoch = self.key_epoch

        ciphertext = self.ciphertext

        deleted = self.deleted

        author_device_id = self.author_device_id

        signed_command = self.signed_command.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "record_id": record_id,
                "kind": kind,
                "revision": revision,
                "cursor": cursor,
                "key_epoch": key_epoch,
                "ciphertext": ciphertext,
                "deleted": deleted,
                "author_device_id": author_device_id,
                "signed_command": signed_command,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_signed_command import E2EeSignedCommand

        d = dict(src_dict)
        record_id = d.pop("record_id")

        kind = E2EeRecordKind(d.pop("kind"))

        revision = d.pop("revision")

        cursor = d.pop("cursor")

        key_epoch = d.pop("key_epoch")

        ciphertext = d.pop("ciphertext")

        deleted = d.pop("deleted")

        author_device_id = d.pop("author_device_id")

        signed_command = E2EeSignedCommand.from_dict(d.pop("signed_command"))

        e2_ee_record = cls(
            record_id=record_id,
            kind=kind,
            revision=revision,
            cursor=cursor,
            key_epoch=key_epoch,
            ciphertext=ciphertext,
            deleted=deleted,
            author_device_id=author_device_id,
            signed_command=signed_command,
        )

        return e2_ee_record
