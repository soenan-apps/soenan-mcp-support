from enum import Enum


class MailLinkAcceptedStatus(str, Enum):
    ACCEPTED = "accepted"

    def __str__(self) -> str:
        return str(self.value)
