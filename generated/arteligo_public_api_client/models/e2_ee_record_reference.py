from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.e2_ee_record_kind import E2EeRecordKind

T = TypeVar("T", bound="E2EeRecordReference")


@_attrs_define
class E2EeRecordReference:
    """
    Attributes:
        record_id (str):
        kind (E2EeRecordKind):
        revision (int):
        cursor (int):
        key_epoch (int):
        deleted (bool):
        author_device_id (str):
        command_id (str): Key into commands; a lookup fingerprint, not a substitute for signature verification.
        ordinal (int): Zero-based record position inside the original signed command body.
    """

    record_id: str
    kind: E2EeRecordKind
    revision: int
    cursor: int
    key_epoch: int
    deleted: bool
    author_device_id: str
    command_id: str
    ordinal: int

    def to_dict(self) -> dict[str, Any]:
        record_id = self.record_id

        kind = self.kind.value

        revision = self.revision

        cursor = self.cursor

        key_epoch = self.key_epoch

        deleted = self.deleted

        author_device_id = self.author_device_id

        command_id = self.command_id

        ordinal = self.ordinal

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "record_id": record_id,
                "kind": kind,
                "revision": revision,
                "cursor": cursor,
                "key_epoch": key_epoch,
                "deleted": deleted,
                "author_device_id": author_device_id,
                "command_id": command_id,
                "ordinal": ordinal,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        record_id = d.pop("record_id")

        kind = E2EeRecordKind(d.pop("kind"))

        revision = d.pop("revision")

        cursor = d.pop("cursor")

        key_epoch = d.pop("key_epoch")

        deleted = d.pop("deleted")

        author_device_id = d.pop("author_device_id")

        command_id = d.pop("command_id")

        ordinal = d.pop("ordinal")

        e2_ee_record_reference = cls(
            record_id=record_id,
            kind=kind,
            revision=revision,
            cursor=cursor,
            key_epoch=key_epoch,
            deleted=deleted,
            author_device_id=author_device_id,
            command_id=command_id,
            ordinal=ordinal,
        )

        return e2_ee_record_reference
