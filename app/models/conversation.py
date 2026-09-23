from datetime import datetime

from sqlmodel import Field, SQLModel

from app.models.common import utc_now


class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=100)
    created_at: datetime = Field(default_factory=utc_now)
