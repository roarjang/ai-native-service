from typing import Annotated
from fastapi import Depends, Header, HTTPException
from app.services.chat_service import ChatService
from app.db import SessionDep
from app.repositories.conversation import ConversationRepository
from app.repositories.message import MessageRepository
from app.services.conversation_service import ConversationService

import os
from functools import lru_cache


from app.llm.base import LLMClient
from app.llm.gemini import GeminiLLMClient


def get_chat_service() -> ChatService:
    return ChatService()


ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]

def require_client_id(
    x_client_id: Annotated[
        str,
        Header(alias="X-Client-Id", min_length=1),
    ],
) -> None:
    if not x_client_id.startswith("student-"):
        raise HTTPException(
            status_code=400,
            detail="X-Client-Id header invalid",
        )

def get_conversation_repository(session: SessionDep) -> ConversationRepository:
    return ConversationRepository(session)


ConversationRepoDep = Annotated[
    ConversationRepository, Depends(get_conversation_repository)
]


def get_message_repository(session: SessionDep) -> MessageRepository:
    return MessageRepository(session)


MessageRepoDep = Annotated[MessageRepository, Depends(get_message_repository)]


def get_conversation_service(
    session: SessionDep,
    conversations: ConversationRepoDep,
    messages: MessageRepoDep,
) -> ConversationService:
    return ConversationService(session, conversations, messages)


ConversationServiceDep = Annotated[
    ConversationService, Depends(get_conversation_service)
]

@lru_cache
def get_llm_client() -> LLMClient:
    model_name = os.environ["LLM_MODEL"]
    return GeminiLLMClient(model_name)


LLMDep = Annotated[LLMClient, Depends(get_llm_client)]


def get_chat_service(llm: LLMDep) -> ChatService:
    return ChatService(llm)


ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]
