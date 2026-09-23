import logging

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import (
    ChatServiceDep,
    ConversationServiceDep,
    require_client_id,
)
from app.schemas.chat import (
    ChatResponse,
    ConversationCreate,
    ConversationRead,
    ConversationUpdate,
    ConversationWithMessages,
    MessageCreate,
)

logger = logging.getLogger(__name__)

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
async def send_message(
    conversation_id: int, request: MessageCreate, service: ChatServiceDep
) -> ChatResponse:
    try:
        return await service.send_message(conversation_id, request)
    except Exception:
        logger.exception("LLM 호출 실패")
        raise HTTPException(
            status_code=502,
            detail="AI 응답을 가져오지 못했습니다.",
        )

@router.post(
    "",
    response_model=ConversationRead,
    status_code=201,
    summary="대화 생성",
)
def create_conversation(
    request: ConversationCreate, service: ConversationServiceDep
) -> ConversationRead:
    return service.create(request.title)


@router.get(
    "",
    response_model=list[ConversationWithMessages],
    summary="대화 목록 조회",
)
def list_conversations(service: ConversationServiceDep) -> list[ConversationWithMessages]:
    return service.list()

@router.patch(
    "/{conversation_id}",
    response_model=ConversationRead,
    summary="대화 제목 수정",
)
def update_conversation(
    conversation_id: int,
    request: ConversationUpdate,
    service: ConversationServiceDep,
) -> ConversationRead:
    row = service.update_title(conversation_id, request.title)
    if row is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return row


@router.delete(
    "/{conversation_id}",
    status_code=204,
    summary="대화 삭제",
)
def delete_conversation(
    conversation_id: int,
    service: ConversationServiceDep,
) -> None:
    if not service.delete(conversation_id):
        raise HTTPException(status_code=404, detail="Conversation not found")
