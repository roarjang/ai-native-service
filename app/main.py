from fastapi import FastAPI
from app.routers import chats


app = FastAPI(title="AI Native Service")
app.include_router(chats.router)
