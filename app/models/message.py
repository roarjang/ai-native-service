from datetime import datetime

from sqlmodel import Field, SQLModel

from app.models.common import utc_now

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: int | None = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id")
    role: str = Field(max_length=20)
    content: str  # TEXT · 길이 제한 없음
    created_at: datetime = Field(default_factory=utc_now)
