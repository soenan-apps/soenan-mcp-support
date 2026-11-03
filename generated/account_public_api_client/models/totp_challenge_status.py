from enum import Enum


class TOTPChallengeStatus(str, Enum):
    TOTP_REQUIRED = "totp_required"

    def __str__(self) -> str:
        return str(self.value)
