from enum import Enum


class AccountProfileEmailVerificationState(str, Enum):
    UNVERIFIED = "unverified"
    VERIFIED = "verified"

    def __str__(self) -> str:
        return str(self.value)
