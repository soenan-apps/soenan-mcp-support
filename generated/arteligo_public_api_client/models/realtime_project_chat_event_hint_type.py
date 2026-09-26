from enum import Enum


class RealtimeProjectChatEventHintType(str, Enum):
    PROJECT_CHAT_EVENT_HINT = "project_chat_event_hint"

    def __str__(self) -> str:
        return str(self.value)
