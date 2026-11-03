from enum import Enum


class PasskeyAuthenticationCredentialAuthenticatorAttachment(str, Enum):
    CROSS_PLATFORM = "cross-platform"
    PLATFORM = "platform"

    def __str__(self) -> str:
        return str(self.value)
