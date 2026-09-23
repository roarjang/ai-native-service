from sqlalchemy.orm import selectinload
from sqlmodel import Session, select


from app.db import engine
from app.models import Conversation, Message




with Session(engine) as session:
   for number in range(1, 4):
       conversation = Conversation(title=f"샘플 대화 {number}")
       session.add(conversation)
       session.flush()
       session.add(
           Message(
               conversation_id=conversation.id,
               role="user",
               content=f"질문 {number}",
           )
       )
       session.add(
           Message(
               conversation_id=conversation.id,
               role="assistant",
               content=f"답변 {number}",
           )
       )
   session.commit()


   print("===== 지연 로딩 =====")
   conversations = session.exec(select(Conversation)).all()
   for conversation in conversations:
       print(conversation.title, len(conversation.messages))


with Session(engine) as session:
   print("===== selectinload =====")
   statement = (
       select(Conversation)
       .options(selectinload(Conversation.messages))
       .order_by(Conversation.created_at.desc())
   )
   conversations = session.exec(statement).all()
   for conversation in conversations:
       print(conversation.title, len(conversation.messages))
