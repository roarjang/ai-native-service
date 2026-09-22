from typing import Annotated
from fastapi import Depends, Header, HTTPException
from app.services.chat_service import ChatService


def get_chat_service() -> ChatService:
    return ChatService()


ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]

def require_client_id(
    x_client_id: Annotated[
        str,
        Header(alias="X-Client-Id", min_length=1),
    ],
) -> None:
    if not x_client_id.startswith("student-"):
        raise HTTPException(
            status_code=400,
            detail="X-Client-Id header invalid",
        )
