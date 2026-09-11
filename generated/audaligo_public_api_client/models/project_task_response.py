from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.project_task import ProjectTask


T = TypeVar("T", bound="ProjectTaskResponse")


@_attrs_define
class ProjectTaskResponse:
    """
    Attributes:
        task (ProjectTask):
    """

    task: ProjectTask

    def to_dict(self) -> dict[str, Any]:
        task = self.task.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "task": task,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.project_task import ProjectTask

        d = dict(src_dict)
        task = ProjectTask.from_dict(d.pop("task"))

        project_task_response = cls(
            task=task,
        )

        return project_task_response
