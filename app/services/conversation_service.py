from sqlmodel import Session

from app.models import Conversation
from app.repositories.conversation import ConversationRepository
from app.repositories.message import MessageRepository


class ConversationService:
    def __init__(
        self,
        session: Session,
        conversations: ConversationRepository,
        messages: MessageRepository,
    ):
        self.session = session
        self.conversations = conversations
        self.messages = messages

    def create(self, title: str, user_id: int | None = None) -> Conversation:
        try:
            conversation = self.conversations.create(title, user_id)
            self.session.commit()
            self.session.refresh(conversation)
            return conversation
        except Exception:
            self.session.rollback()
            raise

    def list_by_user(self, user_id: int) -> list[Conversation]:
        return self.conversations.list_by_user(user_id)

    def list(self) -> list[Conversation]:
        return self.conversations.list_with_messages()

    def start(self, title: str, first_message: str) -> Conversation:
        try:
            conversation = self.conversations.create(title)
            self.messages.create(conversation.id, "user", first_message)
            self.session.commit()
            self.session.refresh(conversation)
            return conversation
        except Exception:
            self.session.rollback()
            raise

    def update_title(self, conversation_id: int, title: str) -> Conversation | None:
        try:
            row = self.conversations.get(conversation_id)
            if row is None:
                return None
            self.conversations.update_title(row, title)
            self.session.commit()
            self.session.refresh(row)
            return row
        except Exception:
            self.session.rollback()
            raise

    def delete(self, conversation_id: int) -> bool:
        try:
            row = self.conversations.get(conversation_id)
            if row is None:
                return False
            self.conversations.delete(row)
            self.session.commit()
            return True
        except Exception:
            self.session.rollback()
            raise
