from enum import Enum


class SignUpConfigurationInvitationMode(str, Enum):
    OPEN = "open"
    OPTIONAL = "optional"
    REQUIRED = "required"

    def __str__(self) -> str:
        return str(self.value)
