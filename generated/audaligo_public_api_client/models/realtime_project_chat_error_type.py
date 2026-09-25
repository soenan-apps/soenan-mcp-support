from enum import Enum


class RealtimeProjectChatErrorType(str, Enum):
    PROJECT_CHAT_ERROR = "project_chat_error"

    def __str__(self) -> str:
        return str(self.value)
