from sqlmodel import Session

from app.dependencies import get_llm_client
from app.llm.fake import FailingLLMClient
from app.main import app
from app.models import Conversation
from app.repositories.ai_execution import ExecutionRepository
from app.repositories.message import MessageRepository

VALID_HEADERS = {"X-Client-Id": "student-01"}


def create_conversation(session: Session) -> Conversation:
    conversation = Conversation(title="통합 테스트 대화")
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation


def message_repo(session: Session) -> MessageRepository:
    return MessageRepository(session)


def execution_repo(session: Session) -> ExecutionRepository:
    return ExecutionRepository(session)


def test_message_success_is_persisted(db_client, session):
    conversation = create_conversation(session)

    response = db_client.post(
        f"/api/conversations/{conversation.id}/messages",
        headers=VALID_HEADERS,
        json={"content": "Repository가 뭐야?"},
    )

    assert response.status_code == 200
    assert response.json()["assistant_message"]["content"] == "통합 테스트 답변"

    messages = message_repo(session).list_by_conversation(conversation.id)
    assert [row.role for row in messages] == ["user", "assistant"]
    assert messages[1].content == "통합 테스트 답변"
    assert execution_repo(session).latest(conversation.id).status == "completed"

def test_llm_failure_is_recorded(db_client, session):
    app.dependency_overrides[get_llm_client] = (
        lambda: FailingLLMClient()
    )
    conversation = create_conversation(session)

    response = db_client.post(
        f"/api/conversations/{conversation.id}/messages",
        headers=VALID_HEADERS,
        json={"content": "실패를 기록해줘"},
    )

    assert response.status_code == 502
    execution = execution_repo(session).latest(conversation.id)
    assert execution.status == "failed"
    assert execution.error_message == "TimeoutError"
    assert [row.role for row in message_repo(session).list_by_conversation(conversation.id)] == ["user"]
