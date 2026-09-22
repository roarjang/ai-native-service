from fastapi import APIRouter

from app.schemas.chat import ChatResponse, MessageCreate
from app.services import chat_service


router = APIRouter(
    prefix="/api/conversations",
    tags=["conversations"],
)


@router.post(
    "/{conversation_id}/messages", response_model=ChatResponse,
    summary="대화에 질문 전송",
    description="사용자 질문을 받고 사용자, AI 메시지를 반환",
)
def send_message(
    conversation_id: int,
    request: MessageCreate,
) -> ChatResponse:
    return chat_service.send_message(conversation_id, request)