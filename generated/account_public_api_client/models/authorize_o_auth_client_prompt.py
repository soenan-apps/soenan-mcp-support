from enum import Enum


class AuthorizeOAuthClientPrompt(str, Enum):
    CONSENT = "consent"

    def __str__(self) -> str:
        return str(self.value)
