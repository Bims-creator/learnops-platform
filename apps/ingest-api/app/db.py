import os

import psycopg

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://learnops:learnops-dev-only@localhost:5432/learnops"
)


def get_connection():
    return psycopg.connect(DATABASE_URL, autocommit=True)


def get_progress(conn, student_id: str):
    cursor = conn.execute(
        """
        SELECT student_id, lessons_completed, average_score, last_event_at
        FROM student_progress
        WHERE student_id = %(student_id)s
        """,
        {"student_id": student_id},
    )
    row = cursor.fetchone()
    if row is None:
        return None
    return {
        "student_id": row[0],
        "lessons_completed": row[1],
        "average_score": row[2],
        "last_event_at": row[3],
    }
