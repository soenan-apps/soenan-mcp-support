from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="E2EeContentMaintenanceCreatedPage")


@_attrs_define
class E2EeContentMaintenanceCreatedPage:
    """
    Attributes:
        record_ids (list[str]):
        has_more (bool):
    """

    record_ids: list[str]
    has_more: bool

    def to_dict(self) -> dict[str, Any]:
        record_ids = self.record_ids

        has_more = self.has_more

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "record_ids": record_ids,
                "has_more": has_more,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        record_ids = cast(list[str], d.pop("record_ids"))

        has_more = d.pop("has_more")

        e2_ee_content_maintenance_created_page = cls(
            record_ids=record_ids,
            has_more=has_more,
        )

        return e2_ee_content_maintenance_created_page
