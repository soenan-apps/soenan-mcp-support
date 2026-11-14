from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast






T = TypeVar("T", bound="InitializeSessionAuthorizationRequest")



@_attrs_define
class InitializeSessionAuthorizationRequest:
    """ 
        Attributes:
            organization_ids (list[str]): Explicit organization scopes to initialize.
            project_ids (list[str]): Projects whose exact owning organization scopes should be initialized. If both selector
                lists are empty, observe current session readiness without contacting Account.
     """

    organization_ids: list[str]
    project_ids: list[str]





    def to_dict(self) -> dict[str, Any]:
        organization_ids = self.organization_ids



        project_ids = self.project_ids




        field_dict: dict[str, Any] = {}

        field_dict.update({
            "organization_ids": organization_ids,
            "project_ids": project_ids,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        organization_ids = cast(list[str], d.pop("organization_ids"))


        project_ids = cast(list[str], d.pop("project_ids"))


        initialize_session_authorization_request = cls(
            organization_ids=organization_ids,
            project_ids=project_ids,
        )

        return initialize_session_authorization_request

