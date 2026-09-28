import json
import logging
from collections.abc import AsyncIterator
from time import perf_counter

from sqlmodel import Session

from app.llm.base import LLMClient
from app.repositories.ai_execution import ExecutionRepository
from app.repositories.conversation import ConversationRepository
from app.repositories.message import MessageRepository
from app.schemas.chat import ChatResponse, MessageCreate, MessageRead
from app.services.errors import ConversationNotFound, LLMUnavailableError

logger = logging.getLogger(__name__)


def stream_event(data: dict[str, str | int]) -> str:
    return json.dumps(data, ensure_ascii=False) + "\n"


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

    def start_stream(self, conversation_id: int, content: str) -> int:
        """Persist the accepted question before sending any response bytes."""
        try:
            if self.conversations.get(conversation_id) is None:
                raise ConversationNotFound(conversation_id)
            self.messages.create(conversation_id, "user", content)
            execution = self.executions.create_running(conversation_id, self.model_name)
            execution_id = execution.id
            self.session.commit()
            return execution_id
        except Exception:
            self.session.rollback()
            raise

    async def stream_reply(
        self, conversation_id: int, content: str, execution_id: int
    ) -> AsyncIterator[str]:
        """Send NDJSON tokens and persist the final answer or failure."""
        answer_parts: list[str] = []
        started = perf_counter()
        try:
            async for chunk in self.llm.stream(content):
                if chunk:
                    answer_parts.append(chunk)
                    yield stream_event({"type": "token", "content": chunk})

            answer = "".join(answer_parts)
            execution = self.executions.get(execution_id)
            assistant = self.messages.create(conversation_id, "assistant", answer)
            self.executions.complete(execution, int((perf_counter() - started) * 1000))
            self.session.commit()
            yield stream_event({"type": "done", "message_id": assistant.id})
        except Exception as exc:
            logger.exception("LLM 스트리밍 실패")
            self.session.rollback()
            execution = self.executions.get(execution_id)
            self.executions.fail(
                execution,
                int((perf_counter() - started) * 1000),
                type(exc).__name__,
            )
            self.session.commit()
            yield stream_event({"type": "error", "code": "LLM_UNAVAILABLE"})
