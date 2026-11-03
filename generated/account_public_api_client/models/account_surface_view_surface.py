from enum import Enum


class AccountSurfaceViewSurface(str, Enum):
    DASHBOARD = "dashboard"
    PROFILE = "profile"

    def __str__(self) -> str:
        return str(self.value)
