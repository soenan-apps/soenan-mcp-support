from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="ManualExternalReference")


@_attrs_define
class ManualExternalReference:
    """
    Attributes:
        source_namespace (str):
        external_reference (str):
    """

    source_namespace: str
    external_reference: str

    def to_dict(self) -> dict[str, Any]:
        source_namespace = self.source_namespace

        external_reference = self.external_reference

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "sourceNamespace": source_namespace,
                "externalReference": external_reference,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        source_namespace = d.pop("sourceNamespace")

        external_reference = d.pop("externalReference")

        manual_external_reference = cls(
            source_namespace=source_namespace,
            external_reference=external_reference,
        )

        return manual_external_reference
