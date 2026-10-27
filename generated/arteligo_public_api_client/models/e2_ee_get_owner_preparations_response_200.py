from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.e2_ee_owner_artifact import E2EeOwnerArtifact


T = TypeVar("T", bound="E2EeGetOwnerPreparationsResponse200")


@_attrs_define
class E2EeGetOwnerPreparationsResponse200:
    """
    Attributes:
        preparations (list[E2EeOwnerArtifact]):
    """

    preparations: list[E2EeOwnerArtifact]

    def to_dict(self) -> dict[str, Any]:
        preparations = []
        for preparations_item_data in self.preparations:
            preparations_item = preparations_item_data.to_dict()
            preparations.append(preparations_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "preparations": preparations,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.e2_ee_owner_artifact import E2EeOwnerArtifact

        d = dict(src_dict)
        preparations = []
        _preparations = d.pop("preparations")
        for preparations_item_data in _preparations:
            preparations_item = E2EeOwnerArtifact.from_dict(preparations_item_data)

            preparations.append(preparations_item)

        e2_ee_get_owner_preparations_response_200 = cls(
            preparations=preparations,
        )

        return e2_ee_get_owner_preparations_response_200
