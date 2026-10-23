from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from dateutil.parser import isoparse
from typing_extensions import Self

T = TypeVar("T", bound="TOTPSetup")


@_attrs_define
class TOTPSetup:
    """
    Attributes:
        secret (str): The 160-bit Authenticator secret encoded as unpadded Base32.
        provisioning_uri (str): Local QR or Authenticator provisioning URI. Never send it to an external QR service.
        expires_at (datetime.datetime):
    """

    secret: str
    provisioning_uri: str
    expires_at: datetime.datetime

    def to_dict(self) -> dict[str, Any]:
        secret = self.secret

        provisioning_uri = self.provisioning_uri

        expires_at = self.expires_at.isoformat()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "secret": secret,
                "provisioningUri": provisioning_uri,
                "expiresAt": expires_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        secret = d.pop("secret")

        provisioning_uri = d.pop("provisioningUri")

        expires_at = isoparse(d.pop("expiresAt"))

        totp_setup = cls(
            secret=secret,
            provisioning_uri=provisioning_uri,
            expires_at=expires_at,
        )

        return totp_setup
