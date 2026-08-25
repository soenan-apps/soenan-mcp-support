from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="ProjectBrief")


@_attrs_define
class ProjectBrief:
    """
    Attributes:
        request_song (None | str | Unset):
        reference_track (None | str | Unset):
        mix_direction (None | str | Unset):
        keep_nuance (None | str | Unset):
    """

    request_song: None | str | Unset = UNSET
    reference_track: None | str | Unset = UNSET
    mix_direction: None | str | Unset = UNSET
    keep_nuance: None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        request_song: None | str | Unset
        if isinstance(self.request_song, Unset):
            request_song = UNSET
        else:
            request_song = self.request_song

        reference_track: None | str | Unset
        if isinstance(self.reference_track, Unset):
            reference_track = UNSET
        else:
            reference_track = self.reference_track

        mix_direction: None | str | Unset
        if isinstance(self.mix_direction, Unset):
            mix_direction = UNSET
        else:
            mix_direction = self.mix_direction

        keep_nuance: None | str | Unset
        if isinstance(self.keep_nuance, Unset):
            keep_nuance = UNSET
        else:
            keep_nuance = self.keep_nuance

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if request_song is not UNSET:
            field_dict["requestSong"] = request_song
        if reference_track is not UNSET:
            field_dict["referenceTrack"] = reference_track
        if mix_direction is not UNSET:
            field_dict["mixDirection"] = mix_direction
        if keep_nuance is not UNSET:
            field_dict["keepNuance"] = keep_nuance

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_request_song(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        request_song = _parse_request_song(d.pop("requestSong", UNSET))

        def _parse_reference_track(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        reference_track = _parse_reference_track(d.pop("referenceTrack", UNSET))

        def _parse_mix_direction(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        mix_direction = _parse_mix_direction(d.pop("mixDirection", UNSET))

        def _parse_keep_nuance(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        keep_nuance = _parse_keep_nuance(d.pop("keepNuance", UNSET))

        project_brief = cls(
            request_song=request_song,
            reference_track=reference_track,
            mix_direction=mix_direction,
            keep_nuance=keep_nuance,
        )

        return project_brief
