import uuid

from worker.db import get_connection, init_db, upsert_event


def test_upsert_event_computes_running_average():
    conn = get_connection()
    init_db(conn)
    student_id = f"pytest-{uuid.uuid4()}"

    upsert_event(conn, {"student_id": student_id, "score": 100, "occurred_at": "2026-01-01T00:00:00Z"})
    upsert_event(conn, {"student_id": student_id, "score": 50, "occurred_at": "2026-01-02T00:00:00Z"})

    row = conn.execute(
        "SELECT lessons_completed, average_score FROM student_progress WHERE student_id = %s",
        (student_id,),
    ).fetchone()
    assert row == (2, 75.0)

    conn.execute("DELETE FROM student_progress WHERE student_id = %s", (student_id,))


def test_upsert_event_handles_missing_score():
    conn = get_connection()
    init_db(conn)
    student_id = f"pytest-{uuid.uuid4()}"

    upsert_event(conn, {"student_id": student_id, "score": None, "occurred_at": "2026-01-01T00:00:00Z"})

    row = conn.execute(
        "SELECT lessons_completed, average_score FROM student_progress WHERE student_id = %s",
        (student_id,),
    ).fetchone()
    assert row == (1, None)

    conn.execute("DELETE FROM student_progress WHERE student_id = %s", (student_id,))
