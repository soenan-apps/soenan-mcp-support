from enum import Enum


class BucketCapabilityContract(str, Enum):
    AUDALIGO_RAILWAY_BUCKET_CAPABILITY = "audaligo.railway-bucket-capability"

    def __str__(self) -> str:
        return str(self.value)
