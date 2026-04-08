from pydantic import BaseModel
from app.schemas.training_type import TrainingTypeResponse
from app.schemas.executed_set import ExecutedSetResponse


class WorkoutUnitCreate(BaseModel):
    training_type_id: str
    total_load_description: str
    notes: str | None = None


class WorkoutUnitUpdate(BaseModel):
    training_type_id: str | None = None
    total_load_description: str | None = None
    notes: str | None = None


class WorkoutUnitResponse(BaseModel):
    id: str
    training_type: TrainingTypeResponse
    executed_sets: list[ExecutedSetResponse]
    total_load_description: str
    notes: str | None = None


class WorkoutUnitSummaryResponse(BaseModel):
    id: str
    training_type: TrainingTypeResponse
