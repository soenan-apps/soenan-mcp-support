from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="E2EeOwnerCustody")


@_attrs_define
class E2EeOwnerCustody:
    """
    Attributes:
        recovery_id (str):
        recovery_generation (int):
        root_revision (int):
        custody_revision (int):
    """

    recovery_id: str
    recovery_generation: int
    root_revision: int
    custody_revision: int

    def to_dict(self) -> dict[str, Any]:
        recovery_id = self.recovery_id

        recovery_generation = self.recovery_generation

        root_revision = self.root_revision

        custody_revision = self.custody_revision

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "recovery_id": recovery_id,
                "recovery_generation": recovery_generation,
                "root_revision": root_revision,
                "custody_revision": custody_revision,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        recovery_id = d.pop("recovery_id")

        recovery_generation = d.pop("recovery_generation")

        root_revision = d.pop("root_revision")

        custody_revision = d.pop("custody_revision")

        e2_ee_owner_custody = cls(
            recovery_id=recovery_id,
            recovery_generation=recovery_generation,
            root_revision=root_revision,
            custody_revision=custody_revision,
        )

        return e2_ee_owner_custody
