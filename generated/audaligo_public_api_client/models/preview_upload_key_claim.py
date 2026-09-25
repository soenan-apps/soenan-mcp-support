from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.preview_upload_key_claim_protocol import PreviewUploadKeyClaimProtocol

T = TypeVar("T", bound="PreviewUploadKeyClaim")


@_attrs_define
class PreviewUploadKeyClaim:
    """
    Attributes:
        url (str):
        expires_at_unix_milliseconds (int):
        protocol (PreviewUploadKeyClaimProtocol):
    """

    url: str
    expires_at_unix_milliseconds: int
    protocol: PreviewUploadKeyClaimProtocol

    def to_dict(self) -> dict[str, Any]:
        url = self.url

        expires_at_unix_milliseconds = self.expires_at_unix_milliseconds

        protocol = self.protocol.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "url": url,
                "expiresAtUnixMilliseconds": expires_at_unix_milliseconds,
                "protocol": protocol,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        url = d.pop("url")

        expires_at_unix_milliseconds = d.pop("expiresAtUnixMilliseconds")

        protocol = PreviewUploadKeyClaimProtocol(d.pop("protocol"))

        preview_upload_key_claim = cls(
            url=url,
            expires_at_unix_milliseconds=expires_at_unix_milliseconds,
            protocol=protocol,
        )

        return preview_upload_key_claim
