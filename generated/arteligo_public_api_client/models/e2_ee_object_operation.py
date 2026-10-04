from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..types import UNSET, Unset

T = TypeVar("T", bound="E2EeObjectOperation")


@_attrs_define
class E2EeObjectOperation:
    """
    Attributes:
        scope_id (str):
        object_id (str):
        index (int | Unset):
    """

    scope_id: str
    object_id: str
    index: int | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        scope_id = self.scope_id

        object_id = self.object_id

        index = self.index

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "scope_id": scope_id,
                "object_id": object_id,
            }
        )
        if index is not UNSET:
            field_dict["index"] = index

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        scope_id = d.pop("scope_id")

        object_id = d.pop("object_id")

        index = d.pop("index", UNSET)

        e2_ee_object_operation = cls(
            scope_id=scope_id,
            object_id=object_id,
            index=index,
        )

        return e2_ee_object_operation
