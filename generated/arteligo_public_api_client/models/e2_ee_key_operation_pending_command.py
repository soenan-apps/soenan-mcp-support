from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.e2_ee_key_operation_pending_command_operation import (
    E2EeKeyOperationPendingCommandOperation,
)

if TYPE_CHECKING:
    from ..models.e2_ee_signed_command import E2EeSignedCommand


T = TypeVar("T", bound="E2EeKeyOperationPendingCommand")


@_attrs_define
class E2EeKeyOperationPendingCommand:
    """
    Attributes:
        operation (E2EeKeyOperationPendingCommandOperation):
        signed_command (E2EeSignedCommand):
    """

    operation: E2EeKeyOperationPendingCommandOperation
    signed_command: E2EeSignedCommand

    def to_dict(self) -> dict[str, Any]:
        operation = self.operation.value

        signed_command = self.signed_command.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "operation": operation,
                "signed_command": signed_command,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.e2_ee_signed_command import E2EeSignedCommand

        d = dict(src_dict)
        operation = E2EeKeyOperationPendingCommandOperation(d.pop("operation"))

        signed_command = E2EeSignedCommand.from_dict(d.pop("signed_command"))

        e2_ee_key_operation_pending_command = cls(
            operation=operation,
            signed_command=signed_command,
        )

        return e2_ee_key_operation_pending_command
