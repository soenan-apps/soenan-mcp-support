from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.project_task_status import ProjectTaskStatus

T = TypeVar("T", bound="ProjectTaskValuesRequest")


@_attrs_define
class ProjectTaskValuesRequest:
    """
    Attributes:
        title (str):
        start_date (datetime.date):
        end_date (datetime.date):
        assignee_membership_id (None | str):
        status (ProjectTaskStatus):
    """

    title: str
    start_date: datetime.date
    end_date: datetime.date
    assignee_membership_id: None | str
    status: ProjectTaskStatus

    def to_dict(self) -> dict[str, Any]:
        title = self.title

        start_date = self.start_date.isoformat()

        end_date = self.end_date.isoformat()

        assignee_membership_id: None | str
        assignee_membership_id = self.assignee_membership_id

        status = self.status.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "title": title,
                "startDate": start_date,
                "endDate": end_date,
                "assigneeMembershipId": assignee_membership_id,
                "status": status,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        title = d.pop("title")

        start_date = datetime.date.fromisoformat(d.pop("startDate"))

        end_date = datetime.date.fromisoformat(d.pop("endDate"))

        def _parse_assignee_membership_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        assignee_membership_id = _parse_assignee_membership_id(
            d.pop("assigneeMembershipId")
        )

        status = ProjectTaskStatus(d.pop("status"))

        project_task_values_request = cls(
            title=title,
            start_date=start_date,
            end_date=end_date,
            assignee_membership_id=assignee_membership_id,
            status=status,
        )

        return project_task_values_request
