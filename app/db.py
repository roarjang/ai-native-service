import os

from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)
