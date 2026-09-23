from sqlmodel import Session, select

from app.models import Message


class MessageRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, conversation_id: int, role: str, content: str) -> Message:
        row = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
        )
        self.session.add(row)
        self.session.flush()
        return row

    def list_by_conversation(self, conversation_id: int) -> list[Message]:
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at, Message.id)
        )
        return list(self.session.exec(statement).all())
