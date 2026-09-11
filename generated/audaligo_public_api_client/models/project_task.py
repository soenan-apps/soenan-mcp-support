from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.project_task_status import ProjectTaskStatus

T = TypeVar("T", bound="ProjectTask")


@_attrs_define
class ProjectTask:
    """
    Attributes:
        id (str):
        project_id (str):
        title (str):
        start_date (datetime.date):
        end_date (datetime.date):
        assignee_membership_id (None | str):
        status (ProjectTaskStatus):
        revision (int):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
    """

    id: str
    project_id: str
    title: str
    start_date: datetime.date
    end_date: datetime.date
    assignee_membership_id: None | str
    status: ProjectTaskStatus
    revision: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        project_id = self.project_id

        title = self.title

        start_date = self.start_date.isoformat()

        end_date = self.end_date.isoformat()

        assignee_membership_id: None | str
        assignee_membership_id = self.assignee_membership_id

        status = self.status.value

        revision = self.revision

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "projectId": project_id,
                "title": title,
                "startDate": start_date,
                "endDate": end_date,
                "assigneeMembershipId": assignee_membership_id,
                "status": status,
                "revision": revision,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        id = d.pop("id")

        project_id = d.pop("projectId")

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

        revision = d.pop("revision")

        created_at = datetime.datetime.fromisoformat(d.pop("createdAt"))

        updated_at = datetime.datetime.fromisoformat(d.pop("updatedAt"))

        project_task = cls(
            id=id,
            project_id=project_id,
            title=title,
            start_date=start_date,
            end_date=end_date,
            assignee_membership_id=assignee_membership_id,
            status=status,
            revision=revision,
            created_at=created_at,
            updated_at=updated_at,
        )

        return project_task
