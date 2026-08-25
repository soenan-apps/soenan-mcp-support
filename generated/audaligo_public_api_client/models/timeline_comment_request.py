from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

T = TypeVar("T", bound="TimelineCommentRequest")


@_attrs_define
class TimelineCommentRequest:
    """
    Attributes:
        version_id (str):
        time_seconds (float):
        end_time_seconds (float | None): Exclusive end of a reviewed time range. Must be greater than timeSeconds when
            present.
        tag (str):
        body (str):
    """

    version_id: str
    time_seconds: float
    end_time_seconds: float | None
    tag: str
    body: str

    def to_dict(self) -> dict[str, Any]:
        version_id = self.version_id

        time_seconds = self.time_seconds

        end_time_seconds: float | None
        end_time_seconds = self.end_time_seconds

        tag = self.tag

        body = self.body

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "versionId": version_id,
                "timeSeconds": time_seconds,
                "endTimeSeconds": end_time_seconds,
                "tag": tag,
                "body": body,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        version_id = d.pop("versionId")

        time_seconds = d.pop("timeSeconds")

        def _parse_end_time_seconds(data: object) -> float | None:
            if data is None:
                return data
            return cast(float | None, data)

        end_time_seconds = _parse_end_time_seconds(d.pop("endTimeSeconds"))

        tag = d.pop("tag")

        body = d.pop("body")

        timeline_comment_request = cls(
            version_id=version_id,
            time_seconds=time_seconds,
            end_time_seconds=end_time_seconds,
            tag=tag,
            body=body,
        )

        return timeline_comment_request
