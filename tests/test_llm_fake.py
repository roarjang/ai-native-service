from fastapi.testclient import TestClient

from app.dependencies import get_llm_client
from app.llm.fake import FakeLLMClient
from app.main import app

URL = "/api/conversations/1/messages"
VALID_HEADERS = {"X-Client-Id": "student-01"}


def test_send_message_uses_fake_llm():
    app.dependency_overrides[get_llm_client] = (
        lambda: FakeLLMClient()
    )
    with TestClient(app) as client:
        response = client.post(
            URL, headers=VALID_HEADERS, json={"content": "테스트 질문"}
        )
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["assistant_message"]["content"] == "테스트용 AI 응답"
