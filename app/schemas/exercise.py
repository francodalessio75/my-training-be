from app.schemas.common import CamelModel
from app.schemas.training_type import TrainingTypeResponse
from app.schemas.muscle_group import MuscleGroupResponse


class ExerciseCreate(CamelModel):
    name: str
    training_type_id: str
    muscle_group_id: str
    execution_description: str
    load_description: str
    notes: str | None = None


class ExerciseUpdate(CamelModel):
    name: str | None = None
    training_type_id: str | None = None
    muscle_group_id: str | None = None
    execution_description: str | None = None
    load_description: str | None = None
    notes: str | None = None


class ExerciseResponse(CamelModel):
    id: str
    name: str
    training_type: TrainingTypeResponse
    muscle_group: MuscleGroupResponse
    execution_description: str
    load_description: str
    notes: str | None = None
