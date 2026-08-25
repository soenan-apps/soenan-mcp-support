from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.responsibility import Responsibility


T = TypeVar("T", bound="ResponsibilityEnvelope")


@_attrs_define
class ResponsibilityEnvelope:
    """
    Attributes:
        responsibility (Responsibility):
    """

    responsibility: Responsibility

    def to_dict(self) -> dict[str, Any]:
        responsibility = self.responsibility.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "responsibility": responsibility,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.responsibility import Responsibility

        d = dict(src_dict)
        responsibility = Responsibility.from_dict(d.pop("responsibility"))

        responsibility_envelope = cls(
            responsibility=responsibility,
        )

        return responsibility_envelope
