from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

T = TypeVar("T", bound="E2EeMember")


@_attrs_define
class E2EeMember:
    """
    Attributes:
        membership_id (str):
        account_subject (str):
        role (str):
        state (str):
    """

    membership_id: str
    account_subject: str
    role: str
    state: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        membership_id = self.membership_id

        account_subject = self.account_subject

        role = self.role

        state = self.state

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "membership_id": membership_id,
                "account_subject": account_subject,
                "role": role,
                "state": state,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        membership_id = d.pop("membership_id")

        account_subject = d.pop("account_subject")

        role = d.pop("role")

        state = d.pop("state")

        e2_ee_member = cls(
            membership_id=membership_id,
            account_subject=account_subject,
            role=role,
            state=state,
        )

        e2_ee_member.additional_properties = d
        return e2_ee_member

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
