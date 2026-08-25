from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="ObjectStateResponse")


@_attrs_define
class ObjectStateResponse:
    """
    Attributes:
        ok (bool):
        object_id (str):
        state (str):
        idempotent (bool | Unset):
    """

    ok: bool
    object_id: str
    state: str
    idempotent: bool | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        ok = self.ok

        object_id = self.object_id

        state = self.state

        idempotent = self.idempotent

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "ok": ok,
                "objectId": object_id,
                "state": state,
            }
        )
        if idempotent is not UNSET:
            field_dict["idempotent"] = idempotent

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        ok = d.pop("ok")

        object_id = d.pop("objectId")

        state = d.pop("state")

        idempotent = d.pop("idempotent", UNSET)

        object_state_response = cls(
            ok=ok,
            object_id=object_id,
            state=state,
            idempotent=idempotent,
        )

        return object_state_response
