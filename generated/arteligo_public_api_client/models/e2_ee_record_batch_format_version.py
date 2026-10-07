from enum import IntEnum


class E2EeRecordBatchFormatVersion(IntEnum):
    VALUE_2 = 2
    VALUE_3 = 3

    def __str__(self) -> str:
        return str(self.value)
