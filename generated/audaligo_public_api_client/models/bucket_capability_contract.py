from enum import StrEnum


class BucketCapabilityContract(StrEnum):
    AUDALIGO_RAILWAY_BUCKET_CAPABILITY = "audaligo.railway-bucket-capability"

    def __str__(self) -> str:
        return str(self.value)
