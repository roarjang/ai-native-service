from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.models.common import utc_now

if TYPE_CHECKING:
    from app.models.ai_execution import AIExecution
    from app.models.message import Message


class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=100)
    created_at: datetime = Field(default_factory=utc_now)

    messages: list["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    executions: list["AIExecution"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    user_id: int | None = Field(
        default=None,
        foreign_key="users.id",
        index=True,
    )