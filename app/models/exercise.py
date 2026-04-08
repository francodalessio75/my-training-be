from beanie import Document, Link
from app.models.training_type import TrainingType
from app.models.muscle_group import MuscleGroup


class Exercise(Document):
    name: str
    training_type: Link[TrainingType]
    muscle_group: Link[MuscleGroup]
    execution_description: str
    load_description: str
    notes: str | None = None

    class Settings:
        name = "exercises"
