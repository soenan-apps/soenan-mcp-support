from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.project_key_ring import ProjectKeyRing


T = TypeVar("T", bound="ProjectKeyRingResponse")


@_attrs_define
class ProjectKeyRingResponse:
    """
    Attributes:
        ok (bool):
        keyring (ProjectKeyRing):
    """

    ok: bool
    keyring: ProjectKeyRing

    def to_dict(self) -> dict[str, Any]:
        ok = self.ok

        keyring = self.keyring.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "ok": ok,
                "keyring": keyring,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.project_key_ring import ProjectKeyRing

        d = dict(src_dict)
        ok = d.pop("ok")

        keyring = ProjectKeyRing.from_dict(d.pop("keyring"))

        project_key_ring_response = cls(
            ok=ok,
            keyring=keyring,
        )

        return project_key_ring_response
