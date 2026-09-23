from datetime import datetime

from sqlmodel import Field, SQLModel

from app.models.common import utc_now


class AIExecution(SQLModel, table=True):
    __tablename__ = "ai_executions"

    id: int | None = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id")
    provider: str = Field(max_length=30)
    model_name: str = Field(max_length=100)
    status: str = Field(max_length=20)
    latency_ms: int | None = None
    error_message: str | None = Field(default=None, max_length=1000)
    created_at: datetime = Field(default_factory=utc_now)
