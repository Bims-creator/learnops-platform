import pytest
from pydantic import ValidationError

from app.schemas import LearningEvent


def test_learning_event_accepts_valid_payload():
    event = LearningEvent(student_id="s1", lesson_id="l1", event_type="lesson_completed", score=92)
    assert event.student_id == "s1"
    assert event.score == 92


def test_learning_event_defaults_occurred_at():
    event = LearningEvent(student_id="s1", lesson_id="l1", event_type="lesson_completed")
    assert event.occurred_at is not None


def test_learning_event_rejects_score_out_of_range():
    with pytest.raises(ValidationError):
        LearningEvent(student_id="s1", lesson_id="l1", event_type="lesson_completed", score=150)
