from beanie import Document


class MuscleGroup(Document):
    name: str
    description: str | None = None

    class Settings:
        name = "muscle-groups"
