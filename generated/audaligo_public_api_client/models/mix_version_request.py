from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.take_audio_role import TakeAudioRole

T = TypeVar("T", bound="MixVersionRequest")


@_attrs_define
class MixVersionRequest:
    """
    Attributes:
        label (str):
        audio_role (TakeAudioRole):
    """

    label: str
    audio_role: TakeAudioRole

    def to_dict(self) -> dict[str, Any]:
        label = self.label

        audio_role = self.audio_role.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "label": label,
                "audioRole": audio_role,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        label = d.pop("label")

        audio_role = TakeAudioRole(d.pop("audioRole"))

        mix_version_request = cls(
            label=label,
            audio_role=audio_role,
        )

        return mix_version_request
