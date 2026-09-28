from app.dependencies import get_llm_client
from app.llm.fake import FakeLLMClient
from app.main import app
from app.models import Conversation

VALID_HEADERS = {"X-Client-Id": "student-01"}


def test_send_message_uses_fake_llm(db_client, session):
    app.dependency_overrides[get_llm_client] = lambda: FakeLLMClient()
    conversation = Conversation(title="가짜 LLM 테스트")
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    response = db_client.post(
        f"/api/conversations/{conversation.id}/messages",
        headers=VALID_HEADERS,
        json={"content": "테스트 질문"},
    )

    assert response.status_code == 200
    assert response.json()["assistant_message"]["content"] == "테스트용 AI 응답"
