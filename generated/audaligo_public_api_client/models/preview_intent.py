from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.preview_intent_media_type import PreviewIntentMediaType
from ..models.preview_intent_profile import PreviewIntentProfile
from ..types import UNSET, Unset

T = TypeVar("T", bound="PreviewIntent")


@_attrs_define
class PreviewIntent:
    """
    Attributes:
        v (int):
        profile (PreviewIntentProfile):
        filename (str):
        media_type (PreviewIntentMediaType):
        plaintext_size (int):
        mix_version_id (str | Unset):
    """

    v: int
    profile: PreviewIntentProfile
    filename: str
    media_type: PreviewIntentMediaType
    plaintext_size: int
    mix_version_id: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        v = self.v

        profile = self.profile.value

        filename = self.filename

        media_type = self.media_type.value

        plaintext_size = self.plaintext_size

        mix_version_id = self.mix_version_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "v": v,
                "profile": profile,
                "filename": filename,
                "mediaType": media_type,
                "plaintextSize": plaintext_size,
            }
        )
        if mix_version_id is not UNSET:
            field_dict["mixVersionId"] = mix_version_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        v = d.pop("v")

        profile = PreviewIntentProfile(d.pop("profile"))

        filename = d.pop("filename")

        media_type = PreviewIntentMediaType(d.pop("mediaType"))

        plaintext_size = d.pop("plaintextSize")

        mix_version_id = d.pop("mixVersionId", UNSET)

        preview_intent = cls(
            v=v,
            profile=profile,
            filename=filename,
            media_type=media_type,
            plaintext_size=plaintext_size,
            mix_version_id=mix_version_id,
        )

        return preview_intent
