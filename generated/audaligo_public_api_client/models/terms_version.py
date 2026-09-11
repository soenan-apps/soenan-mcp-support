from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="TermsVersion")


@_attrs_define
class TermsVersion:
    """
    Attributes:
        id (str): Opaque immutable Audaligo terms version identifier.
        version_label (str):
        title (str):
        body (str): Immutable plain-text Audaligo service terms.
        body_sha_256 (str): Lowercase hexadecimal encoding of exactly one SHA-256 digest.
        language_tag (str):
        published_at (datetime.datetime):
        effective_at (datetime.datetime):
    """

    id: str
    version_label: str
    title: str
    body: str
    body_sha_256: str
    language_tag: str
    published_at: datetime.datetime
    effective_at: datetime.datetime

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        version_label = self.version_label

        title = self.title

        body = self.body

        body_sha_256 = self.body_sha_256

        language_tag = self.language_tag

        published_at = self.published_at.isoformat()

        effective_at = self.effective_at.isoformat()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "versionLabel": version_label,
                "title": title,
                "body": body,
                "bodySha256": body_sha_256,
                "languageTag": language_tag,
                "publishedAt": published_at,
                "effectiveAt": effective_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        id = d.pop("id")

        version_label = d.pop("versionLabel")

        title = d.pop("title")

        body = d.pop("body")

        body_sha_256 = d.pop("bodySha256")

        language_tag = d.pop("languageTag")

        published_at = datetime.datetime.fromisoformat(d.pop("publishedAt"))

        effective_at = datetime.datetime.fromisoformat(d.pop("effectiveAt"))

        terms_version = cls(
            id=id,
            version_label=version_label,
            title=title,
            body=body,
            body_sha_256=body_sha_256,
            language_tag=language_tag,
            published_at=published_at,
            effective_at=effective_at,
        )

        return terms_version
