from typing import Literal
from pydantic import BaseModel, Field
from datetime import datetime


class ConversationCreate(BaseModel):
    title: str = Field(
        min_length=1, max_length=100
    )


class MessageCreate(BaseModel):
    content: str = Field(
        min_length=1, max_length=2000,
        description="사용자 질문",
        examples=["FastAPI 프로젝트 구조를 설명해 줘"],
    )


class MessageRead(BaseModel):
    id: int
    role: Literal["user", "assistant"]
    content: str


class ChatResponse(BaseModel):
    conversation_id: int
    user_message: MessageRead
    assistant_message: MessageRead

class ConversationRead(BaseModel):
    id: int
    title: str
    created_at: datetime


class ConversationWithMessages(ConversationRead):
    messages: list[MessageRead]


class ConversationUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
