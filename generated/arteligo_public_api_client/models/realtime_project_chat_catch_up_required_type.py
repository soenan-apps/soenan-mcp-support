from enum import Enum


class RealtimeProjectChatCatchUpRequiredType(str, Enum):
    PROJECT_CHAT_CATCH_UP_REQUIRED = "project_chat_catch_up_required"

    def __str__(self) -> str:
        return str(self.value)
