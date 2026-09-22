from fastapi import APIRouter, Depends

from app.dependencies import ChatServiceDep, require_client_id
from app.schemas.chat import ChatResponse, MessageCreate

router = APIRouter(
    prefix="/api/conversations",
    tags=["conversations"],
    dependencies=[Depends(require_client_id)],
)

@router.post(
    "/{conversation_id}/messages",
    response_model=ChatResponse,
    summary="대화에 질문 전송",
    description="사용자 질문을 받고 사용자·AI 메시지를 반환",
)
def send_message(
    conversation_id: int, request: MessageCreate, service: ChatServiceDep
) -> ChatResponse:
    return service.send_message(conversation_id, request)
