from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.e2_ee_project_key_state import E2EeProjectKeyState
from ..types import UNSET, Unset

T = TypeVar("T", bound="E2EeProject")


@_attrs_define
class E2EeProject:
    """
    Attributes:
        project_id (str):
        participation_policy (str):
        role (str):
        lifecycle (str): Content lifecycle, independent from key readiness.
        key_state (E2EeProjectKeyState): Key initialization or required rotation, independent from content lifecycle.
        key_epoch (int):
        revision (int):
        owner_org (str | Unset):
        owner_key_maintenance (bool | Unset): Narrow inherited Owner key authority. Does not grant content writes or
            invitations.
    """

    project_id: str
    participation_policy: str
    role: str
    lifecycle: str
    key_state: E2EeProjectKeyState
    key_epoch: int
    revision: int
    owner_org: str | Unset = UNSET
    owner_key_maintenance: bool | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        project_id = self.project_id

        participation_policy = self.participation_policy

        role = self.role

        lifecycle = self.lifecycle

        key_state = self.key_state.value

        key_epoch = self.key_epoch

        revision = self.revision

        owner_org = self.owner_org

        owner_key_maintenance = self.owner_key_maintenance

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "project_id": project_id,
                "participation_policy": participation_policy,
                "role": role,
                "lifecycle": lifecycle,
                "key_state": key_state,
                "key_epoch": key_epoch,
                "revision": revision,
            }
        )
        if owner_org is not UNSET:
            field_dict["owner_org"] = owner_org
        if owner_key_maintenance is not UNSET:
            field_dict["owner_key_maintenance"] = owner_key_maintenance

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        project_id = d.pop("project_id")

        participation_policy = d.pop("participation_policy")

        role = d.pop("role")

        lifecycle = d.pop("lifecycle")

        key_state = E2EeProjectKeyState(d.pop("key_state"))

        key_epoch = d.pop("key_epoch")

        revision = d.pop("revision")

        owner_org = d.pop("owner_org", UNSET)

        owner_key_maintenance = d.pop("owner_key_maintenance", UNSET)

        e2_ee_project = cls(
            project_id=project_id,
            participation_policy=participation_policy,
            role=role,
            lifecycle=lifecycle,
            key_state=key_state,
            key_epoch=key_epoch,
            revision=revision,
            owner_org=owner_org,
            owner_key_maintenance=owner_key_maintenance,
        )

        return e2_ee_project
