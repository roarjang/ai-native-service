import json

from app.dependencies import get_llm_client
from app.llm.fake import FailingLLMClient
from app.main import app
from app.models import Conversation
from app.repositories.ai_execution import ExecutionRepository
from app.repositories.message import MessageRepository


HEADERS = {"X-Client-Id": "student-01"}


def create_conversation(session):
    conversation = Conversation(title="스트리밍 테스트")
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation


def events(response):
    return [json.loads(line) for line in response.text.splitlines()]


def test_stream_persists_reply_and_execution(db_client, session):
    conversation = create_conversation(session)

    response = db_client.post(
        f"/api/conversations/{conversation.id}/messages/stream",
        headers=HEADERS,
        json={"content": "Repository가 뭐야?"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/x-ndjson")
    assert [event["type"] for event in events(response)] == ["token", "done"]
    assert events(response)[0]["content"] == "통합 테스트 답변"
    messages = MessageRepository(session).list_by_conversation(conversation.id)
    assert [message.role for message in messages] == ["user", "assistant"]
    assert messages[1].content == "통합 테스트 답변"
    assert events(response)[1]["message_id"] == messages[1].id
    assert ExecutionRepository(session).latest(conversation.id).status == "completed"


def test_stream_records_failure_after_user_message(db_client, session):
    app.dependency_overrides[get_llm_client] = lambda: FailingLLMClient()
    conversation = create_conversation(session)

    response = db_client.post(
        f"/api/conversations/{conversation.id}/messages/stream",
        headers=HEADERS,
        json={"content": "실패를 기록해줘"},
    )

    assert response.status_code == 200
    assert events(response) == [{"type": "error", "code": "LLM_UNAVAILABLE"}]
    messages = MessageRepository(session).list_by_conversation(conversation.id)
    assert [message.role for message in messages] == ["user"]
    execution = ExecutionRepository(session).latest(conversation.id)
    assert execution.status == "failed"
    assert execution.error_message == "TimeoutError"


def test_stream_rejects_missing_conversation_before_response(db_client):
    response = db_client.post(
        "/api/conversations/999999/messages/stream",
        headers=HEADERS,
        json={"content": "질문"},
    )
    assert response.status_code == 404
