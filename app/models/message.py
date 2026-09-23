from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.models.common import utc_now

if TYPE_CHECKING:
    from app.models.conversation import Conversation

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: int | None = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id")
    role: str = Field(max_length=20)
    content: str  # TEXT · 길이 제한 없음
    created_at: datetime = Field(default_factory=utc_now)

    conversation: "Conversation" = Relationship(
        back_populates="messages"
    )