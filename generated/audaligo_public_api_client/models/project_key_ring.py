from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.project_key_ring_contract import ProjectKeyRingContract
from ..models.project_key_ring_v import ProjectKeyRingV

if TYPE_CHECKING:
    from ..models.project_key_epoch_material import ProjectKeyEpochMaterial


T = TypeVar("T", bound="ProjectKeyRing")


@_attrs_define
class ProjectKeyRing:
    """
    Attributes:
        v (ProjectKeyRingV):
        contract (ProjectKeyRingContract):
        project_id (str):
        current_epoch (int):
        keys (list[ProjectKeyEpochMaterial]):
    """

    v: ProjectKeyRingV
    contract: ProjectKeyRingContract
    project_id: str
    current_epoch: int
    keys: list[ProjectKeyEpochMaterial]

    def to_dict(self) -> dict[str, Any]:
        v = self.v.value

        contract = self.contract.value

        project_id = self.project_id

        current_epoch = self.current_epoch

        keys = []
        for keys_item_data in self.keys:
            keys_item = keys_item_data.to_dict()
            keys.append(keys_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "v": v,
                "contract": contract,
                "projectId": project_id,
                "currentEpoch": current_epoch,
                "keys": keys,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.project_key_epoch_material import (
            ProjectKeyEpochMaterial,
        )

        d = dict(src_dict)
        v = ProjectKeyRingV(d.pop("v"))

        contract = ProjectKeyRingContract(d.pop("contract"))

        project_id = d.pop("projectId")

        current_epoch = d.pop("currentEpoch")

        keys = []
        _keys = d.pop("keys")
        for keys_item_data in _keys:
            keys_item = ProjectKeyEpochMaterial.from_dict(keys_item_data)

            keys.append(keys_item)

        project_key_ring = cls(
            v=v,
            contract=contract,
            project_id=project_id,
            current_epoch=current_epoch,
            keys=keys,
        )

        return project_key_ring
