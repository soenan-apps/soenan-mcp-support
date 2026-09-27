from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.bucket_capability import BucketCapability


T = TypeVar("T", bound="CapabilityResponse")


@_attrs_define
class CapabilityResponse:
    """
    Attributes:
        capability (BucketCapability):
    """

    capability: BucketCapability

    def to_dict(self) -> dict[str, Any]:
        capability = self.capability.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "capability": capability,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.bucket_capability import BucketCapability

        d = dict(src_dict)
        capability = BucketCapability.from_dict(d.pop("capability"))

        capability_response = cls(
            capability=capability,
        )

        return capability_response
