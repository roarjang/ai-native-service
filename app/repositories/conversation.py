from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.models import Conversation


class ConversationRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, title: str, user_id: int | None = None) -> Conversation:
        row = Conversation(title=title, user_id=user_id)
        self.session.add(row)
        self.session.flush()
        self.session.refresh(row)
        return row

    def get(self, conversation_id: int) -> Conversation | None:
        return self.session.get(Conversation, conversation_id)

    # ── 여기부터 3단계 ──────────────────────────────
    def list_with_messages(self) -> list[Conversation]:
        statement = (
            select(Conversation)
            .options(selectinload(Conversation.messages))
            .order_by(Conversation.created_at.desc())
        )
        return list(self.session.exec(statement).all())

    def update_title(self, row: Conversation, title: str) -> Conversation:
        row.title = title
        self.session.add(row)
        self.session.flush()
        return row

    def delete(self, row: Conversation) -> None:
        self.session.delete(row)
        self.session.flush()

    def list_by_user(self, user_id: int) -> list[Conversation]:
        statement = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .options(selectinload(Conversation.messages))
            .order_by(Conversation.created_at.desc())
        )
        return list(self.session.exec(statement).all())
