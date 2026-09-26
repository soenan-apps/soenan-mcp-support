from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.project_task import ProjectTask


T = TypeVar("T", bound="ProjectTaskListResponse")


@_attrs_define
class ProjectTaskListResponse:
    """
    Attributes:
        tasks (list[ProjectTask]):
        next_cursor (None | str):
    """

    tasks: list[ProjectTask]
    next_cursor: None | str

    def to_dict(self) -> dict[str, Any]:
        tasks = []
        for tasks_item_data in self.tasks:
            tasks_item = tasks_item_data.to_dict()
            tasks.append(tasks_item)

        next_cursor: None | str
        next_cursor = self.next_cursor

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "tasks": tasks,
                "nextCursor": next_cursor,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.project_task import ProjectTask

        d = dict(src_dict)
        tasks = []
        _tasks = d.pop("tasks")
        for tasks_item_data in _tasks:
            tasks_item = ProjectTask.from_dict(tasks_item_data)

            tasks.append(tasks_item)

        def _parse_next_cursor(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        next_cursor = _parse_next_cursor(d.pop("nextCursor"))

        project_task_list_response = cls(
            tasks=tasks,
            next_cursor=next_cursor,
        )

        return project_task_list_response
