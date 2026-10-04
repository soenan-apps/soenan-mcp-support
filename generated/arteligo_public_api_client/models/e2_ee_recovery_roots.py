from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.e2_ee_recovery_public import E2EeRecoveryPublic


T = TypeVar("T", bound="E2EeRecoveryRoots")


@_attrs_define
class E2EeRecoveryRoots:
    """
    Attributes:
        recoveries (list[E2EeRecoveryPublic]):
    """

    recoveries: list[E2EeRecoveryPublic]

    def to_dict(self) -> dict[str, Any]:
        recoveries = []
        for recoveries_item_data in self.recoveries:
            recoveries_item = recoveries_item_data.to_dict()
            recoveries.append(recoveries_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "recoveries": recoveries,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_recovery_public import E2EeRecoveryPublic

        d = dict(src_dict)
        recoveries = []
        _recoveries = d.pop("recoveries")
        for recoveries_item_data in _recoveries:
            recoveries_item = E2EeRecoveryPublic.from_dict(recoveries_item_data)

            recoveries.append(recoveries_item)

        e2_ee_recovery_roots = cls(
            recoveries=recoveries,
        )

        return e2_ee_recovery_roots
