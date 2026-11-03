from enum import Enum


class MCPOAuthScope(str, Enum):
    ACCOUNTREAD = "account:read"
    ACCOUNTWRITE = "account:write"
    ARTELIGOREAD = "arteligo:read"
    ARTELIGOWRITE = "arteligo:write"

    def __str__(self) -> str:
        return str(self.value)
