from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.e2_ee_signed_command import E2EeSignedCommand


T = TypeVar("T", bound="E2EeCommandProof")


@_attrs_define
class E2EeCommandProof:
    """
    Attributes:
        operation (str):
        command (E2EeSignedCommand):
    """

    operation: str
    command: E2EeSignedCommand

    def to_dict(self) -> dict[str, Any]:
        operation = self.operation

        command = self.command.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "operation": operation,
                "command": command,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_signed_command import E2EeSignedCommand

        d = dict(src_dict)
        operation = d.pop("operation")

        command = E2EeSignedCommand.from_dict(d.pop("command"))

        e2_ee_command_proof = cls(
            operation=operation,
            command=command,
        )

        return e2_ee_command_proof
