from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.e2_ee_signed_command import E2EeSignedCommand


T = TypeVar("T", bound="E2EeTrustStatements")


@_attrs_define
class E2EeTrustStatements:
    """
    Attributes:
        statements (list[E2EeSignedCommand]):
    """

    statements: list[E2EeSignedCommand]

    def to_dict(self) -> dict[str, Any]:
        statements = []
        for statements_item_data in self.statements:
            statements_item = statements_item_data.to_dict()
            statements.append(statements_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "statements": statements,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_signed_command import E2EeSignedCommand

        d = dict(src_dict)
        statements = []
        _statements = d.pop("statements")
        for statements_item_data in _statements:
            statements_item = E2EeSignedCommand.from_dict(statements_item_data)

            statements.append(statements_item)

        e2_ee_trust_statements = cls(
            statements=statements,
        )

        return e2_ee_trust_statements
