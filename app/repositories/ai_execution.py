from sqlmodel import Session, select

from app.models import AIExecution


class ExecutionRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_running(self, conversation_id: int, model: str) -> AIExecution:
        row = AIExecution(
            conversation_id=conversation_id,
            provider=model.split("/", 1)[0],
            model_name=model,
            status="running",
        )
        self.session.add(row)
        self.session.flush()
        return row

    def complete(self, row: AIExecution, latency_ms: int) -> AIExecution:
        row.status = "completed"
        row.latency_ms = latency_ms
        self.session.add(row)
        self.session.flush()
        return row

    def fail(self, row: AIExecution, latency_ms: int, error: str) -> AIExecution:
        row.status = "failed"
        row.latency_ms = latency_ms
        row.error_message = error
        self.session.add(row)
        self.session.flush()
        return row

    def list_by_conversation(self, conversation_id: int) -> list[AIExecution]:
        statement = (
            select(AIExecution)
            .where(AIExecution.conversation_id == conversation_id)
            .order_by(AIExecution.created_at.desc(), AIExecution.id.desc())
        )
        return list(self.session.exec(statement).all())

    def latest(self, conversation_id: int) -> AIExecution | None:
        rows = self.list_by_conversation(conversation_id)
        return rows[0] if rows else None

    def get(self, execution_id: int) -> AIExecution | None:
        return self.session.get(AIExecution, execution_id)
