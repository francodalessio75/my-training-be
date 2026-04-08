from beanie import Document


class TrainingType(Document):
    name: str
    description: str

    class Settings:
        name = "training-types"
