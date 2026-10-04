from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.e2_ee_record_kind import E2EeRecordKind

T = TypeVar("T", bound="E2EeRecordWrite")


@_attrs_define
class E2EeRecordWrite:
    """
    Attributes:
        record_id (str):
        kind (E2EeRecordKind):
        expected_revision (int):
        key_epoch (int):
        ciphertext (str):
        deleted (bool):
    """

    record_id: str
    kind: E2EeRecordKind
    expected_revision: int
    key_epoch: int
    ciphertext: str
    deleted: bool

    def to_dict(self) -> dict[str, Any]:
        record_id = self.record_id

        kind = self.kind.value

        expected_revision = self.expected_revision

        key_epoch = self.key_epoch

        ciphertext = self.ciphertext

        deleted = self.deleted

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "record_id": record_id,
                "kind": kind,
                "expected_revision": expected_revision,
                "key_epoch": key_epoch,
                "ciphertext": ciphertext,
                "deleted": deleted,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        record_id = d.pop("record_id")

        kind = E2EeRecordKind(d.pop("kind"))

        expected_revision = d.pop("expected_revision")

        key_epoch = d.pop("key_epoch")

        ciphertext = d.pop("ciphertext")

        deleted = d.pop("deleted")

        e2_ee_record_write = cls(
            record_id=record_id,
            kind=kind,
            expected_revision=expected_revision,
            key_epoch=key_epoch,
            ciphertext=ciphertext,
            deleted=deleted,
        )

        return e2_ee_record_write
