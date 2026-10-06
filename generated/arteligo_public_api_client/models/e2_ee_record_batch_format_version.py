from enum import IntEnum


class E2EeRecordBatchFormatVersion(IntEnum):
    VALUE_2 = 2

    def __str__(self) -> str:
        return str(self.value)
