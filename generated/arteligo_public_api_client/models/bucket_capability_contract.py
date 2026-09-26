from enum import Enum


class BucketCapabilityContract(str, Enum):
    ARTELIGO_RAILWAY_BUCKET_CAPABILITY = "arteligo.railway-bucket-capability"

    def __str__(self) -> str:
        return str(self.value)
