from datetime import datetime, timezone

from pydantic import BaseModel, Field


class LearningEvent(BaseModel):
    student_id: str
    lesson_id: str
    event_type: str = Field(description="e.g. 'lesson_completed', 'quiz_submitted'")
    score: float | None = Field(default=None, ge=0, le=100)
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
