from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.e2_ee_owner_generation_operation import E2EeOwnerGenerationOperation

if TYPE_CHECKING:
    from ..models.e2_ee_owner_authority import E2EeOwnerAuthority
    from ..models.e2_ee_signed_command import E2EeSignedCommand


T = TypeVar("T", bound="E2EeOwnerGeneration")


@_attrs_define
class E2EeOwnerGeneration:
    """
    Attributes:
        key_epoch (int):
        owner_authority (E2EeOwnerAuthority):
        signed_command (E2EeSignedCommand):
        operation (E2EeOwnerGenerationOperation):
    """

    key_epoch: int
    owner_authority: E2EeOwnerAuthority
    signed_command: E2EeSignedCommand
    operation: E2EeOwnerGenerationOperation

    def to_dict(self) -> dict[str, Any]:
        key_epoch = self.key_epoch

        owner_authority = self.owner_authority.to_dict()

        signed_command = self.signed_command.to_dict()

        operation = self.operation.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "key_epoch": key_epoch,
                "owner_authority": owner_authority,
                "signed_command": signed_command,
                "operation": operation,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.e2_ee_owner_authority import E2EeOwnerAuthority
        from ..models.e2_ee_signed_command import E2EeSignedCommand

        d = dict(src_dict)
        key_epoch = d.pop("key_epoch")

        owner_authority = E2EeOwnerAuthority.from_dict(d.pop("owner_authority"))

        signed_command = E2EeSignedCommand.from_dict(d.pop("signed_command"))

        operation = E2EeOwnerGenerationOperation(d.pop("operation"))

        e2_ee_owner_generation = cls(
            key_epoch=key_epoch,
            owner_authority=owner_authority,
            signed_command=signed_command,
            operation=operation,
        )

        return e2_ee_owner_generation
