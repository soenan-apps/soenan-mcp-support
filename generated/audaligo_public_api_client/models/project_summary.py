from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.project_participation_policy import ProjectParticipationPolicy
from ..models.project_summary_status import ProjectSummaryStatus
from ..types import UNSET, Unset, parse_datetime

if TYPE_CHECKING:
    from ..models.responsibility import Responsibility


T = TypeVar("T", bound="ProjectSummary")


@_attrs_define
class ProjectSummary:
    """
    Attributes:
        id (str):
        slug (str):
        title (str):
        participation_policy (ProjectParticipationPolicy): Controls who may participate in the project as an Editor.
            Organization includes current members of the Owner organization; private includes only the Owner and
            individually invited Editors. Every participant has the same project capabilities except Owner-only invitation
            and member management.
        status (ProjectSummaryStatus):
        progress (float):
        responsibility (Responsibility):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
        deadline_date (None | str | Unset):
    """

    id: str
    slug: str
    title: str
    participation_policy: ProjectParticipationPolicy
    status: ProjectSummaryStatus
    progress: float
    responsibility: Responsibility
    created_at: datetime.datetime
    updated_at: datetime.datetime
    deadline_date: None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        slug = self.slug

        title = self.title

        participation_policy = self.participation_policy.value

        status = self.status.value

        progress = self.progress

        responsibility = self.responsibility.to_dict()

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        deadline_date: None | str | Unset
        if isinstance(self.deadline_date, Unset):
            deadline_date = UNSET
        else:
            deadline_date = self.deadline_date

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "slug": slug,
                "title": title,
                "participationPolicy": participation_policy,
                "status": status,
                "progress": progress,
                "responsibility": responsibility,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )
        if deadline_date is not UNSET:
            field_dict["deadlineDate"] = deadline_date

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.responsibility import Responsibility

        d = dict(src_dict)
        id = d.pop("id")

        slug = d.pop("slug")

        title = d.pop("title")

        participation_policy = ProjectParticipationPolicy(d.pop("participationPolicy"))

        status = ProjectSummaryStatus(d.pop("status"))

        progress = d.pop("progress")

        responsibility = Responsibility.from_dict(d.pop("responsibility"))

        created_at = parse_datetime(d.pop("createdAt"))

        updated_at = parse_datetime(d.pop("updatedAt"))

        def _parse_deadline_date(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        deadline_date = _parse_deadline_date(d.pop("deadlineDate", UNSET))

        project_summary = cls(
            id=id,
            slug=slug,
            title=title,
            participation_policy=participation_policy,
            status=status,
            progress=progress,
            responsibility=responsibility,
            created_at=created_at,
            updated_at=updated_at,
            deadline_date=deadline_date,
        )

        return project_summary
