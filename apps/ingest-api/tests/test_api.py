"""Integration tests: require Postgres + Redis reachable (docker compose up -d locally,
service containers in CI). Do not run these with aggregator-worker also draining the
queue - they'll race for the same Redis list.
"""
import uuid

from fastapi.testclient import TestClient

from app.db import get_connection
from app.main import app
from app.redis_client import EVENTS_QUEUE_KEY, client as redis_client

client = TestClient(app)


def test_healthz():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readyz_reaches_redis_and_postgres():
    response = client.get("/readyz")
    assert response.status_code == 200


def test_post_event_queues_to_redis():
    student_id = f"pytest-{uuid.uuid4()}"
    response = client.post(
        "/events",
        json={"student_id": student_id, "lesson_id": "l1", "event_type": "lesson_completed", "score": 75},
    )
    assert response.status_code == 202

    _, raw = redis_client.blpop(EVENTS_QUEUE_KEY, timeout=2)
    assert student_id in raw


def test_get_progress_returns_seeded_row():
    student_id = f"pytest-{uuid.uuid4()}"
    conn = get_connection()
    conn.execute(
        "INSERT INTO student_progress (student_id, lessons_completed, average_score, last_event_at) "
        "VALUES (%s, 3, 88.5, now())",
        (student_id,),
    )

    response = client.get(f"/progress/{student_id}")
    assert response.status_code == 200
    assert response.json()["lessons_completed"] == 3

    conn.execute("DELETE FROM student_progress WHERE student_id = %s", (student_id,))


def test_get_progress_404_for_unknown_student():
    response = client.get("/progress/does-not-exist-at-all-really")
    assert response.status_code == 404
