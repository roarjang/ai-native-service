from app.llm.base import LLMClient
from app.schemas.chat import ChatResponse, MessageCreate, MessageRead


class ChatService:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    async def send_message(
        self,
        conversation_id: int,
        request: MessageCreate,
    ) -> ChatResponse:
        prompt = (
            "다음 질문에 초보 개발자가 이해할 수 있게 "
            f"세 문장으로 답해줘.\n질문: {request.content}"
        )
        answer = await self.llm.generate(prompt)
        user_message = MessageRead(
            id=1, role="user", content=request.content
        )
        assistant_message = MessageRead(
            id=2, role="assistant", content=answer
        )
        return ChatResponse(
            conversation_id=conversation_id,
            user_message=user_message,
            assistant_message=assistant_message,
        )
