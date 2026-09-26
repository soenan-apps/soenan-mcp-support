from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="ProjectBriefRequest")


@_attrs_define
class ProjectBriefRequest:
    """
    Attributes:
        request_song (str):
        reference_track (str):
        mix_direction (str):
        keep_nuance (str):
    """

    request_song: str
    reference_track: str
    mix_direction: str
    keep_nuance: str

    def to_dict(self) -> dict[str, Any]:
        request_song = self.request_song

        reference_track = self.reference_track

        mix_direction = self.mix_direction

        keep_nuance = self.keep_nuance

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "requestSong": request_song,
                "referenceTrack": reference_track,
                "mixDirection": mix_direction,
                "keepNuance": keep_nuance,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        request_song = d.pop("requestSong")

        reference_track = d.pop("referenceTrack")

        mix_direction = d.pop("mixDirection")

        keep_nuance = d.pop("keepNuance")

        project_brief_request = cls(
            request_song=request_song,
            reference_track=reference_track,
            mix_direction=mix_direction,
            keep_nuance=keep_nuance,
        )

        return project_brief_request
