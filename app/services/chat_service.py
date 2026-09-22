from app.schemas.chat import ChatResponse, MessageCreate, MessageRead

class ChatService:
    def send_message(
        self,
        conversation_id: int,
        request: MessageCreate,
    ) -> ChatResponse:
        user_message = MessageRead(
            id=1, role="user", content=request.content
        )
        assistant_message = MessageRead(
            id=2, role="assistant", content="AI 응답 예시"
        )
        return ChatResponse(
            conversation_id=conversation_id,
            user_message=user_message,
            assistant_message=assistant_message,
        )
