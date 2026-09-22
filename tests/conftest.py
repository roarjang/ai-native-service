import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_chat_service
from app.main import app
from app.schemas.chat import ChatResponse, MessageRead


class FakeChatService:
    def send_message(self, conversation_id, request):
        return ChatResponse(
            conversation_id=conversation_id,
            user_message=MessageRead(
                id=10, role="user", content=request.content
            ),
            assistant_message=MessageRead(
                id=20, role="assistant", content="테스트 응답"
            ),
        )


def override_chat_service():
    return FakeChatService()


@pytest.fixture
def client():
    app.dependency_overrides[get_chat_service] = (
        override_chat_service
    )
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
