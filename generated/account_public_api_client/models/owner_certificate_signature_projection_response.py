from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.owner_certificate_signature_projection import (
        OwnerCertificateSignatureProjection,
    )


T = TypeVar("T", bound="OwnerCertificateSignatureProjectionResponse")


@_attrs_define
class OwnerCertificateSignatureProjectionResponse:
    """
    Attributes:
        challenge (str):
        projection (OwnerCertificateSignatureProjection):
    """

    challenge: str
    projection: OwnerCertificateSignatureProjection

    def to_dict(self) -> dict[str, Any]:
        challenge = self.challenge

        projection = self.projection.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "challenge": challenge,
                "projection": projection,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.owner_certificate_signature_projection import (
            OwnerCertificateSignatureProjection,
        )

        d = dict(src_dict)
        challenge = d.pop("challenge")

        projection = OwnerCertificateSignatureProjection.from_dict(d.pop("projection"))

        owner_certificate_signature_projection_response = cls(
            challenge=challenge,
            projection=projection,
        )

        return owner_certificate_signature_projection_response
