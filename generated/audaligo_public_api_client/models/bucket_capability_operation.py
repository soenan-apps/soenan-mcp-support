from enum import StrEnum


class BucketCapabilityOperation(StrEnum):
    GET = "GET"
    PUT = "PUT"

    def __str__(self) -> str:
        return str(self.value)
