from app.schemas.common import CamelModel
from app.schemas.exercise import ExerciseResponse


class ExecutedSetCreate(CamelModel):
    exercise_id: str
    load: float
    load_description: str
    repetitions: int
    notes: str | None = None


class ExecutedSetUpdate(CamelModel):
    exercise_id: str | None = None
    load: float | None = None
    load_description: str | None = None
    repetitions: int | None = None
    notes: str | None = None


class ExecutedSetResponse(CamelModel):
    id: str
    exercise: ExerciseResponse
    load: float
    load_description: str
    repetitions: int
    notes: str | None = None
