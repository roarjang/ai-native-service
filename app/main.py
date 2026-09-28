from pathlib import Path

from fastapi import FastAPI
from app.routers import chats


app = FastAPI(title="AI Native Service")
app.include_router(chats.router)

frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if frontend_dist.is_dir():
    app.frontend("/", directory=frontend_dist, fallback="index.html")
