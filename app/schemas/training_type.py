from pydantic import BaseModel


class TrainingTypeCreate(BaseModel):
    name: str
    description: str


class TrainingTypeUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class TrainingTypeResponse(BaseModel):
    id: str
    name: str
    description: str
