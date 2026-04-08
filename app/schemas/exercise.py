from pydantic import BaseModel
from app.schemas.training_type import TrainingTypeResponse
from app.schemas.muscle_group import MuscleGroupResponse


class ExerciseCreate(BaseModel):
    name: str
    training_type_id: str
    muscle_group_id: str
    execution_description: str
    load_description: str
    notes: str | None = None


class ExerciseUpdate(BaseModel):
    name: str | None = None
    training_type_id: str | None = None
    muscle_group_id: str | None = None
    execution_description: str | None = None
    load_description: str | None = None
    notes: str | None = None


class ExerciseResponse(BaseModel):
    id: str
    name: str
    training_type: TrainingTypeResponse
    muscle_group: MuscleGroupResponse
    execution_description: str
    load_description: str
    notes: str | None = None
