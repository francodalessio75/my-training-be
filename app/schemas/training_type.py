from app.schemas.common import CamelModel


class TrainingTypeCreate(CamelModel):
    name: str
    description: str


class TrainingTypeUpdate(CamelModel):
    name: str | None = None
    description: str | None = None


class TrainingTypeResponse(CamelModel):
    id: str
    name: str
    description: str
