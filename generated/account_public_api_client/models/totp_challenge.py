from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.totp_challenge_status import TOTPChallengeStatus

T = TypeVar("T", bound="TOTPChallenge")


@_attrs_define
class TOTPChallenge:
    """Opaque acknowledgement that does not disclose account eligibility or whether a tracked challenge exists. Never sends
    mail.

        Attributes:
            status (TOTPChallengeStatus):
            challenge_id (str):
    """

    status: TOTPChallengeStatus
    challenge_id: str

    def to_dict(self) -> dict[str, Any]:
        status = self.status.value

        challenge_id = self.challenge_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "status": status,
                "challengeId": challenge_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        status = TOTPChallengeStatus(d.pop("status"))

        challenge_id = d.pop("challengeId")

        totp_challenge = cls(
            status=status,
            challenge_id=challenge_id,
        )

        return totp_challenge
