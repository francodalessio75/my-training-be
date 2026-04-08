from pydantic import BaseModel
from app.schemas.exercise import ExerciseResponse


class ExecutedSetCreate(BaseModel):
    exercise_id: str
    load: float
    load_description: str
    repetitions: int
    notes: str | None = None


class ExecutedSetUpdate(BaseModel):
    exercise_id: str | None = None
    load: float | None = None
    load_description: str | None = None
    repetitions: int | None = None
    notes: str | None = None


class ExecutedSetResponse(BaseModel):
    id: str
    exercise: ExerciseResponse
    load: float
    load_description: str
    repetitions: int
    notes: str | None = None
