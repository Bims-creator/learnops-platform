from fastapi import FastAPI, HTTPException

from app.db import get_connection, get_progress
from app.redis_client import EVENTS_QUEUE_KEY, client as redis_client
from app.schemas import LearningEvent

app = FastAPI(title="learnops-ingest-api")
db_conn = get_connection()


@app.get("/healthz")
def healthz():
    """Liveness: is the process up at all."""
    return {"status": "ok"}


@app.get("/readyz")
def readyz():
    """Readiness: can we actually reach Redis and Postgres."""
    redis_client.ping()
    db_conn.execute("SELECT 1")
    return {"status": "ready"}


@app.post("/events", status_code=202)
def ingest_event(event: LearningEvent):
    redis_client.rpush(EVENTS_QUEUE_KEY, event.model_dump_json())
    return {"queued": True}


@app.get("/progress/{student_id}")
def read_progress(student_id: str):
    progress = get_progress(db_conn, student_id)
    if progress is None:
        raise HTTPException(status_code=404, detail="No progress recorded for this student")
    return progress
