from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..types import UNSET, Unset

T = TypeVar("T", bound="E2EeProject")


@_attrs_define
class E2EeProject:
    """
    Attributes:
        project_id (str):
        participation_policy (str):
        role (str):
        lifecycle (str):
        key_epoch (int):
        revision (int):
        owner_org (str | Unset):
    """

    project_id: str
    participation_policy: str
    role: str
    lifecycle: str
    key_epoch: int
    revision: int
    owner_org: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        project_id = self.project_id

        participation_policy = self.participation_policy

        role = self.role

        lifecycle = self.lifecycle

        key_epoch = self.key_epoch

        revision = self.revision

        owner_org = self.owner_org

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "project_id": project_id,
                "participation_policy": participation_policy,
                "role": role,
                "lifecycle": lifecycle,
                "key_epoch": key_epoch,
                "revision": revision,
            }
        )
        if owner_org is not UNSET:
            field_dict["owner_org"] = owner_org

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        project_id = d.pop("project_id")

        participation_policy = d.pop("participation_policy")

        role = d.pop("role")

        lifecycle = d.pop("lifecycle")

        key_epoch = d.pop("key_epoch")

        revision = d.pop("revision")

        owner_org = d.pop("owner_org", UNSET)

        e2_ee_project = cls(
            project_id=project_id,
            participation_policy=participation_policy,
            role=role,
            lifecycle=lifecycle,
            key_epoch=key_epoch,
            revision=revision,
            owner_org=owner_org,
        )

        return e2_ee_project
