class ConversationNotFound(Exception):
    def __init__(self, conversation_id: int):
        super().__init__(f"conversation {conversation_id} not found")
        self.conversation_id = conversation_id


class LLMUnavailableError(Exception):
    pass
