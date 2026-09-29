import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import chats
from app.settings import settings

logger = logging.getLogger(__name__)
FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("app_env=%s", settings.app_env)
    # logger.info("key=%s", settings.gemini_api_key.get_secret_value())  # 금지
    yield


app = FastAPI(title="AI Native Service", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chats.router)


@app.get("/health", include_in_schema=False)
def health() -> dict[str, str]:
    return {"status": "ok"}


if FRONTEND_DIST.is_dir():
    app.frontend("/", directory=FRONTEND_DIST, fallback="index.html")
