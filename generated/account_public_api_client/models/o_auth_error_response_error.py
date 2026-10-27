from enum import Enum


class OAuthErrorResponseError(str, Enum):
    ACCESS_DENIED = "access_denied"
    INVALID_CLIENT = "invalid_client"
    INVALID_GRANT = "invalid_grant"
    INVALID_REDIRECT_URI = "invalid_redirect_uri"
    INVALID_REQUEST = "invalid_request"
    INVALID_SCOPE = "invalid_scope"
    TEMPORARILY_UNAVAILABLE = "temporarily_unavailable"
    UNSUPPORTED_GRANT_TYPE = "unsupported_grant_type"

    def __str__(self) -> str:
        return str(self.value)
