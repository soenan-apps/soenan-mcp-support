from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..types import UNSET, Unset

T = TypeVar("T", bound="E2EeRecordPrecondition")


@_attrs_define
class E2EeRecordPrecondition:
    """
    Attributes:
        record_id (str):
        expected_revision (int):
        require_live (bool | Unset):  Default: True.
    """

    record_id: str
    expected_revision: int
    require_live: bool | Unset = True

    def to_dict(self) -> dict[str, Any]:
        record_id = self.record_id

        expected_revision = self.expected_revision

        require_live = self.require_live

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "record_id": record_id,
                "expected_revision": expected_revision,
            }
        )
        if require_live is not UNSET:
            field_dict["require_live"] = require_live

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        record_id = d.pop("record_id")

        expected_revision = d.pop("expected_revision")

        require_live = d.pop("require_live", UNSET)

        e2_ee_record_precondition = cls(
            record_id=record_id,
            expected_revision=expected_revision,
            require_live=require_live,
        )

        return e2_ee_record_precondition
