from enum import Enum


class RealtimeProjectChatSubscribedType(str, Enum):
    PROJECT_CHAT_SUBSCRIBED = "project_chat_subscribed"

    def __str__(self) -> str:
        return str(self.value)
