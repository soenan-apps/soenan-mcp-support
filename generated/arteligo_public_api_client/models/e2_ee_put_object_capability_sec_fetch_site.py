from enum import Enum


class E2EePutObjectCapabilitySecFetchSite(str, Enum):
    SAME_ORIGIN = "same-origin"

    def __str__(self) -> str:
        return str(self.value)
