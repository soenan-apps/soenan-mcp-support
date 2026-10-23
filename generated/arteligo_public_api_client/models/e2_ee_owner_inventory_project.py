from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.e2_ee_signed_command import E2EeSignedCommand


T = TypeVar("T", bound="E2EeOwnerInventoryProject")


@_attrs_define
class E2EeOwnerInventoryProject:
    """
    Attributes:
        project_id (str):
        lifecycle (str):
        key_epoch (int):
        epochs (list[int]):
        creation_command (E2EeSignedCommand):
    """

    project_id: str
    lifecycle: str
    key_epoch: int
    epochs: list[int]
    creation_command: E2EeSignedCommand

    def to_dict(self) -> dict[str, Any]:
        project_id = self.project_id

        lifecycle = self.lifecycle

        key_epoch = self.key_epoch

        epochs = self.epochs

        creation_command = self.creation_command.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "project_id": project_id,
                "lifecycle": lifecycle,
                "key_epoch": key_epoch,
                "epochs": epochs,
                "creation_command": creation_command,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_signed_command import E2EeSignedCommand

        d = dict(src_dict)
        project_id = d.pop("project_id")

        lifecycle = d.pop("lifecycle")

        key_epoch = d.pop("key_epoch")

        epochs = cast(list[int], d.pop("epochs"))

        creation_command = E2EeSignedCommand.from_dict(d.pop("creation_command"))

        e2_ee_owner_inventory_project = cls(
            project_id=project_id,
            lifecycle=lifecycle,
            key_epoch=key_epoch,
            epochs=epochs,
            creation_command=creation_command,
        )

        return e2_ee_owner_inventory_project
