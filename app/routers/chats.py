import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.dependencies import (
    ChatServiceDep,
    ConversationRepoDep,
    ConversationServiceDep,
    ExecutionRepoDep,
    MessageRepoDep,
    require_client_id,
)
from app.schemas.chat import (
    ChatResponse,
    ConversationCreate,
    ConversationRead,
    ConversationUpdate,
    ConversationWithMessages,
    ExecutionRead,
    MessageCreate,
    MessageRead,
)
from app.services.errors import ConversationNotFound, LLMUnavailableError
from app.auth import get_current_user
from app.models.user import User


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
    except ConversationNotFound as exc:
        raise HTTPException(404, "대화를 찾을 수 없습니다.") from exc
    except LLMUnavailableError as exc:
        logger.exception("LLM 호출 실패")
        raise HTTPException(502, "AI 응답을 가져오지 못했습니다.") from exc


@router.post("/{conversation_id}/messages/stream")
async def stream_message(
    conversation_id: int, request: MessageCreate, service: ChatServiceDep
) -> StreamingResponse:
    try:
        execution_id = service.start_stream(conversation_id, request.content)
    except ConversationNotFound as exc:
        raise HTTPException(404, "대화를 찾을 수 없습니다.") from exc
    return StreamingResponse(
        service.stream_reply(conversation_id, request.content, execution_id),
        media_type="application/x-ndjson",
    )


@router.post(
    "",
    response_model=ConversationRead,
    status_code=201,
    summary="대화 생성",
)
def create_conversation(
    request: ConversationCreate,
    service: ConversationServiceDep,
    user: User = Depends(get_current_user),
) -> ConversationRead:
    return service.create(request.title, user.id)


@router.get(
    "",
    response_model=list[ConversationWithMessages],
    summary="대화 목록 조회",
)
def list_conversations(
    service: ConversationServiceDep,
    user: User = Depends(get_current_user),
) -> list[ConversationWithMessages]:
    return service.list_by_user(user.id)

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


@router.get("/{conversation_id}/messages", response_model=list[MessageRead])
def list_messages(
    conversation_id: int,
    conversations: ConversationRepoDep,
    messages: MessageRepoDep,
    user: User = Depends(get_current_user),
):
    conversation = conversations.get(conversation_id)
    if conversation is None or conversation.user_id != user.id:
        raise HTTPException(404, "대화를 찾을 수 없습니다.")
    return messages.list_by_conversation(conversation_id)


@router.get("/{conversation_id}/executions", response_model=list[ExecutionRead])
def list_executions(
    conversation_id: int,
    conversations: ConversationRepoDep,
    executions: ExecutionRepoDep,
):
    if conversations.get(conversation_id) is None:
        raise HTTPException(404, "대화를 찾을 수 없습니다.")
    return executions.list_by_conversation(conversation_id)
