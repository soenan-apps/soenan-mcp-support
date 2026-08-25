from enum import Enum


class PreviewFailureReason(str, Enum):
    INPUT_TOO_LARGE = "input_too_large"
    OUTPUT_TOO_LARGE = "output_too_large"
    PROCESSING_FAILED = "processing_failed"
    QUOTA_EXCEEDED = "quota_exceeded"
    UNSUPPORTED_AUDIO = "unsupported_audio"

    def __str__(self) -> str:
        return str(self.value)
