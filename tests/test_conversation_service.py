from unittest.mock import MagicMock

import pytest

from app.services.conversation_service import ConversationService


def test_start_rolls_back_when_message_fails():
    session = MagicMock()
    conversations = MagicMock()
    messages = MagicMock()
    service = ConversationService(session, conversations, messages)
    messages.create.side_effect = RuntimeError("저장 실패")

    with pytest.raises(RuntimeError):
        service.start("새 대화", "질문")

    session.rollback.assert_called_once()
    session.commit.assert_not_called()
