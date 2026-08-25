from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.file_key_claim_protocol import FileKeyClaimProtocol

T = TypeVar("T", bound="FileKeyClaim")


@_attrs_define
class FileKeyClaim:
    """
    Attributes:
        url (str):
        expires_at_unix_milliseconds (int):
        protocol (FileKeyClaimProtocol):
    """

    url: str
    expires_at_unix_milliseconds: int
    protocol: FileKeyClaimProtocol

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
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        url = d.pop("url")

        expires_at_unix_milliseconds = d.pop("expiresAtUnixMilliseconds")

        protocol = FileKeyClaimProtocol(d.pop("protocol"))

        file_key_claim = cls(
            url=url,
            expires_at_unix_milliseconds=expires_at_unix_milliseconds,
            protocol=protocol,
        )

        return file_key_claim
