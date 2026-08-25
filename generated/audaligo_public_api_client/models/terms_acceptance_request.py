from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="TermsAcceptanceRequest")


@_attrs_define
class TermsAcceptanceRequest:
    """
    Attributes:
        terms_version_id (str): Opaque immutable Audaligo terms version identifier.
    """

    terms_version_id: str

    def to_dict(self) -> dict[str, Any]:
        terms_version_id = self.terms_version_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "termsVersionId": terms_version_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        terms_version_id = d.pop("termsVersionId")

        terms_acceptance_request = cls(
            terms_version_id=terms_version_id,
        )

        return terms_acceptance_request
