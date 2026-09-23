import os
import pytest

from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine

from app.main import app
from app.db import get_session
from app.dependencies import get_llm_client, get_chat_service
from app.llm.fake import FakeLLMClient
from app.schemas.chat import ChatResponse, MessageRead

from fastapi.testclient import TestClient


load_dotenv()

TEST_DATABASE_URL = os.environ["TEST_DATABASE_URL"]
if not TEST_DATABASE_URL.rsplit("/", 1)[-1].endswith("_test"):
    raise RuntimeError("테스트 DB 이름의 _test 접미사 누락")

test_engine = create_engine(TEST_DATABASE_URL)


class FakeChatService:
    async def send_message(self, conversation_id, request):
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

@pytest.fixture
def session():
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        yield session
    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture
def db_client(session: Session):
    def get_test_session():
        return session

    app.dependency_overrides[get_session] = get_test_session
    app.dependency_overrides[get_llm_client] = (
        lambda: FakeLLMClient("통합 테스트 답변")
    )

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
