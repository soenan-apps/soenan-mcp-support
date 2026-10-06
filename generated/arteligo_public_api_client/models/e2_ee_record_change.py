from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.e2_ee_record_kind import E2EeRecordKind

T = TypeVar("T", bound="E2EeRecordChange")


@_attrs_define
class E2EeRecordChange:
    """
    Attributes:
        record_id (str):
        kind (E2EeRecordKind):
        revision (int):
        cursor (int):
        key_epoch (int):
        deleted (bool):
        transaction_first_cursor (int):
        transaction_last_cursor (int):
    """

    record_id: str
    kind: E2EeRecordKind
    revision: int
    cursor: int
    key_epoch: int
    deleted: bool
    transaction_first_cursor: int
    transaction_last_cursor: int

    def to_dict(self) -> dict[str, Any]:
        record_id = self.record_id

        kind = self.kind.value

        revision = self.revision

        cursor = self.cursor

        key_epoch = self.key_epoch

        deleted = self.deleted

        transaction_first_cursor = self.transaction_first_cursor

        transaction_last_cursor = self.transaction_last_cursor

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "record_id": record_id,
                "kind": kind,
                "revision": revision,
                "cursor": cursor,
                "key_epoch": key_epoch,
                "deleted": deleted,
                "transaction_first_cursor": transaction_first_cursor,
                "transaction_last_cursor": transaction_last_cursor,
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

        transaction_first_cursor = d.pop("transaction_first_cursor")

        transaction_last_cursor = d.pop("transaction_last_cursor")

        e2_ee_record_change = cls(
            record_id=record_id,
            kind=kind,
            revision=revision,
            cursor=cursor,
            key_epoch=key_epoch,
            deleted=deleted,
            transaction_first_cursor=transaction_first_cursor,
            transaction_last_cursor=transaction_last_cursor,
        )

        return e2_ee_record_change
