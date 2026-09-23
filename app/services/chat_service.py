from time import perf_counter

from sqlmodel import Session

from app.llm.base import LLMClient
from app.repositories.ai_execution import ExecutionRepository
from app.repositories.conversation import ConversationRepository
from app.repositories.message import MessageRepository
from app.schemas.chat import ChatResponse, MessageCreate, MessageRead
from app.services.errors import ConversationNotFound, LLMUnavailableError


class ChatService:
    def __init__(
        self,
        session: Session,
        conversations: ConversationRepository,
        messages: MessageRepository,
        executions: ExecutionRepository,
        llm: LLMClient,
        model_name: str,
    ):
        self.session = session
        self.conversations = conversations
        self.messages = messages
        self.executions = executions
        self.llm = llm
        self.model_name = model_name

    async def send_message(
        self,
        conversation_id: int,
        request: MessageCreate,
    ) -> ChatResponse:
        # ── 트랜잭션 A ─────────────────────────────────
        conversation = self.conversations.get(conversation_id)
        if conversation is None:
            raise ConversationNotFound(conversation_id)

        user_message = self.messages.create(conversation_id, "user", request.content)
        execution = self.executions.create_running(
            conversation_id,
            self.model_name,
        )
        self.session.commit()

        # ── 외부 호출 (트랜잭션 밖) ────────────────────
        started = perf_counter()
        try:
            answer = await self.llm.generate(request.content)
            latency_ms = int((perf_counter() - started) * 1000)

            # ── 트랜잭션 B · 성공 ──────────────────────
            assistant_message = self.messages.create(
                conversation_id,
                "assistant",
                answer,
            )
            self.executions.complete(execution, latency_ms)
            self.session.commit()
        except Exception as exc:
            # ── 트랜잭션 B · 실패 ──────────────────────
            self.session.rollback()
            latency_ms = int((perf_counter() - started) * 1000)

            safe_error = type(exc).__name__
            self.executions.fail(execution, latency_ms, safe_error)
            self.session.commit()
            raise LLMUnavailableError() from exc

        return ChatResponse(
            conversation_id=conversation_id,
            user_message=MessageRead(
                id=user_message.id, role="user", content=user_message.content
            ),
            assistant_message=MessageRead(
                id=assistant_message.id,
                role="assistant",
                content=assistant_message.content,
            ),
        )
