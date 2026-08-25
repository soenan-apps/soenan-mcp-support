from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.take_audio_role import TakeAudioRole
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.file_check import FileCheck
    from ..models.member_actor import MemberActor


T = TypeVar("T", bound="MixVersion")


@_attrs_define
class MixVersion:
    """
    Attributes:
        id (str):
        kind (str):
        audio_role (TakeAudioRole):
        creator (MemberActor):
        upload_state (str):
        label (str):
        checks (list[FileCheck]):
        file_name (None | str | Unset):
        ab_score (float | None | Unset):
        ab_value (None | str | Unset):
    """

    id: str
    kind: str
    audio_role: TakeAudioRole
    creator: MemberActor
    upload_state: str
    label: str
    checks: list[FileCheck]
    file_name: None | str | Unset = UNSET
    ab_score: float | None | Unset = UNSET
    ab_value: None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        kind = self.kind

        audio_role = self.audio_role.value

        creator = self.creator.to_dict()

        upload_state = self.upload_state

        label = self.label

        checks = []
        for checks_item_data in self.checks:
            checks_item = checks_item_data.to_dict()
            checks.append(checks_item)

        file_name: None | str | Unset
        if isinstance(self.file_name, Unset):
            file_name = UNSET
        else:
            file_name = self.file_name

        ab_score: float | None | Unset
        if isinstance(self.ab_score, Unset):
            ab_score = UNSET
        else:
            ab_score = self.ab_score

        ab_value: None | str | Unset
        if isinstance(self.ab_value, Unset):
            ab_value = UNSET
        else:
            ab_value = self.ab_value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "kind": kind,
                "audioRole": audio_role,
                "creator": creator,
                "uploadState": upload_state,
                "label": label,
                "checks": checks,
            }
        )
        if file_name is not UNSET:
            field_dict["fileName"] = file_name
        if ab_score is not UNSET:
            field_dict["abScore"] = ab_score
        if ab_value is not UNSET:
            field_dict["abValue"] = ab_value

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.file_check import FileCheck
        from ..models.member_actor import MemberActor

        d = dict(src_dict)
        id = d.pop("id")

        kind = d.pop("kind")

        audio_role = TakeAudioRole(d.pop("audioRole"))

        creator = MemberActor.from_dict(d.pop("creator"))

        upload_state = d.pop("uploadState")

        label = d.pop("label")

        checks = []
        _checks = d.pop("checks")
        for checks_item_data in _checks:
            checks_item = FileCheck.from_dict(checks_item_data)

            checks.append(checks_item)

        def _parse_file_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        file_name = _parse_file_name(d.pop("fileName", UNSET))

        def _parse_ab_score(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        ab_score = _parse_ab_score(d.pop("abScore", UNSET))

        def _parse_ab_value(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        ab_value = _parse_ab_value(d.pop("abValue", UNSET))

        mix_version = cls(
            id=id,
            kind=kind,
            audio_role=audio_role,
            creator=creator,
            upload_state=upload_state,
            label=label,
            checks=checks,
            file_name=file_name,
            ab_score=ab_score,
            ab_value=ab_value,
        )

        return mix_version
