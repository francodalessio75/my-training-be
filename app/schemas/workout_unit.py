from app.schemas.common import CamelModel
from app.schemas.training_type import TrainingTypeResponse
from app.schemas.executed_set import ExecutedSetResponse


class WorkoutUnitCreate(CamelModel):
    training_type_id: str
    total_load_description: str
    notes: str | None = None


class WorkoutUnitUpdate(CamelModel):
    training_type_id: str | None = None
    total_load_description: str | None = None
    notes: str | None = None


class WorkoutUnitResponse(CamelModel):
    id: str
    training_type: TrainingTypeResponse
    executed_sets: list[ExecutedSetResponse]
    total_load_description: str
    notes: str | None = None


class WorkoutUnitSummaryResponse(CamelModel):
    id: str
    training_type: TrainingTypeResponse
