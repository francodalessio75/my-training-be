from uuid import UUID, uuid4
from datetime import datetime
from beanie import Document, Link
from pydantic import BaseModel, Field
from app.models.training_type import TrainingType
from app.models.exercise import Exercise


class ExecutedSet(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    exercise: Link[Exercise]
    load: float
    load_description: str
    repetitions: int
    notes: str | None = None


class WorkoutUnit(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    training_type: Link[TrainingType]
    executed_sets: list[ExecutedSet] = []
    total_load_description: str
    notes: str | None = None


class Session(Document):
    user_id: str
    name: str
    date: datetime
    workout_units: list[WorkoutUnit] = []
    total_load_description: str
    notes: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "sessions"
