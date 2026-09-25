from enum import Enum


class BucketCapabilityOperation(str, Enum):
    GET = "GET"
    PUT = "PUT"

    def __str__(self) -> str:
        return str(self.value)
