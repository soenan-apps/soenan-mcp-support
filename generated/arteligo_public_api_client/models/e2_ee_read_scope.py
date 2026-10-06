from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="E2EeReadScope")


@_attrs_define
class E2EeReadScope:
    """
    Attributes:
        scope_id (str):
        record_ids (list[str]):
    """

    scope_id: str
    record_ids: list[str]

    def to_dict(self) -> dict[str, Any]:
        scope_id = self.scope_id

        record_ids = self.record_ids

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "scope_id": scope_id,
                "record_ids": record_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        scope_id = d.pop("scope_id")

        record_ids = cast(list[str], d.pop("record_ids"))

        e2_ee_read_scope = cls(
            scope_id=scope_id,
            record_ids=record_ids,
        )

        return e2_ee_read_scope
