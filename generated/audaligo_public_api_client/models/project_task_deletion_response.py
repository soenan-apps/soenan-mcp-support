from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="ProjectTaskDeletionResponse")


@_attrs_define
class ProjectTaskDeletionResponse:
    """
    Attributes:
        deleted_task_id (str):
    """

    deleted_task_id: str

    def to_dict(self) -> dict[str, Any]:
        deleted_task_id = self.deleted_task_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "deletedTaskId": deleted_task_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        deleted_task_id = d.pop("deletedTaskId")

        project_task_deletion_response = cls(
            deleted_task_id=deleted_task_id,
        )

        return project_task_deletion_response
