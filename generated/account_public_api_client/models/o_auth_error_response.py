from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.o_auth_error_response_error import OAuthErrorResponseError
from ..types import UNSET, Unset

T = TypeVar("T", bound="OAuthErrorResponse")


@_attrs_define
class OAuthErrorResponse:
    """
    Attributes:
        error (OAuthErrorResponseError):
        error_description (str | Unset):
        state (str | Unset):
    """

    error: OAuthErrorResponseError
    error_description: str | Unset = UNSET
    state: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        error = self.error.value

        error_description = self.error_description

        state = self.state

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "error": error,
            }
        )
        if error_description is not UNSET:
            field_dict["error_description"] = error_description
        if state is not UNSET:
            field_dict["state"] = state

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        error = OAuthErrorResponseError(d.pop("error"))

        error_description = d.pop("error_description", UNSET)

        state = d.pop("state", UNSET)

        o_auth_error_response = cls(
            error=error,
            error_description=error_description,
            state=state,
        )

        return o_auth_error_response
