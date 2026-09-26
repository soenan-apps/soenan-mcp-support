from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="UpdateProjectDeadlineRequest")


@_attrs_define
class UpdateProjectDeadlineRequest:
    """
    Attributes:
        deadline_date (None | str):
    """

    deadline_date: None | str

    def to_dict(self) -> dict[str, Any]:
        deadline_date: None | str
        deadline_date = self.deadline_date

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "deadlineDate": deadline_date,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)

        def _parse_deadline_date(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        deadline_date = _parse_deadline_date(d.pop("deadlineDate"))

        update_project_deadline_request = cls(
            deadline_date=deadline_date,
        )

        return update_project_deadline_request
