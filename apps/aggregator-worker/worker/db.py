import os

import psycopg

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://learnops:learnops-dev-only@localhost:5432/learnops"
)


def get_connection():
    return psycopg.connect(DATABASE_URL, autocommit=True)


def init_db(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS student_progress (
            student_id TEXT PRIMARY KEY,
            lessons_completed INT NOT NULL DEFAULT 0,
            scored_events INT NOT NULL DEFAULT 0,
            total_score DOUBLE PRECISION NOT NULL DEFAULT 0,
            average_score DOUBLE PRECISION,
            last_event_at TIMESTAMPTZ
        )
    """)


def upsert_event(conn, event: dict):
    conn.execute(
        """
        INSERT INTO student_progress
            (student_id, lessons_completed, scored_events, total_score, average_score, last_event_at)
        VALUES (
            %(student_id)s,
            1,
            CASE WHEN %(score)s::double precision IS NULL THEN 0 ELSE 1 END,
            COALESCE(%(score)s::double precision, 0),
            %(score)s::double precision,
            %(occurred_at)s
        )
        ON CONFLICT (student_id) DO UPDATE SET
            lessons_completed = student_progress.lessons_completed + 1,
            scored_events = student_progress.scored_events
                + CASE WHEN %(score)s::double precision IS NULL THEN 0 ELSE 1 END,
            total_score = student_progress.total_score + COALESCE(%(score)s::double precision, 0),
            average_score = (student_progress.total_score + COALESCE(%(score)s::double precision, 0))
                / NULLIF(
                    student_progress.scored_events
                        + CASE WHEN %(score)s::double precision IS NULL THEN 0 ELSE 1 END,
                    0
                  ),
            last_event_at = %(occurred_at)s
        """,
        {
            "student_id": event["student_id"],
            "score": event.get("score"),
            "occurred_at": event["occurred_at"],
        },
    )
